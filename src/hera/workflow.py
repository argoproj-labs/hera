"""The implementation of a Hera workflow for Argo-based workflows"""
import json
from types import ModuleType
from typing import Any, Dict, List, Optional, Tuple, TypeVar, Union

from argo_workflows.model_utils import model_to_dict
from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1Arguments,
    IoArgoprojWorkflowV1alpha1VolumeClaimGC,
    IoArgoprojWorkflowV1alpha1Workflow,
    IoArgoprojWorkflowV1alpha1WorkflowSpec,
    LocalObjectReference,
    ObjectMeta,
)

import hera
from hera.affinity import Affinity
from hera.dag import DAG
from hera.global_config import GlobalConfig
from hera.host_alias import HostAlias
from hera.metric import Metric, Metrics
from hera.parameter import Parameter
from hera.security_context import WorkflowSecurityContext
from hera.task import Task
from hera.toleration import Toleration
from hera.ttl_strategy import TTLStrategy
from hera.validators import validate_name
from hera.volume_claim_gc import VolumeClaimGCStrategy
from hera.workflow_service import WorkflowService

# PyYAML is an optional dependency
_yaml: Optional[ModuleType] = None
try:
    import yaml

    _yaml = yaml
except ImportError:
    _yaml = None

WorkflowType = TypeVar("WorkflowType", bound="Workflow")


class Workflow:
    """A workflow representation.

    The workflow is used as a functional representation for a collection of tasks and
    steps. The workflow context controls the overall behaviour of tasks, such as whether to notify completion, whether
    to execute retires, overall parallelism, etc. The workflow can be constructed and submitted to multiple Argo
    endpoints as long as a token can be associated with the endpoint at the given domain.

    Parameters
    ----------
    name: str
        The workflow name. Note that the workflow initiation will replace underscores with dashes.
    dag_name: Optional[str] = None
        Name of the underlying dag template. This will default to the name of the workflow.
    service: Optional[WorkflowService] = None
        A workflow service to use for submissions. See `hera.v1.workflow_service.WorkflowService`.
    parallelism: Optional[int] = None
        The number of parallel tasks to run in case a task group is executed for multiple tasks.
    service_account_name: Optional[str] = None,
        The name of the service account to use in all workflow tasks.
    labels: Optional[Dict[str, str]] = None
        A dictionary of labels to attach to the Workflow object metadata.
    annotations: Optional[Dict[str, str]] = None
        A dictionary of annotations to attach to the Workflow object metadata.
    security_context: Optional[WorkflowSecurityContext] = None
        Define security settings for all containers in the workflow.
    image_pull_secrets: Optional[List[str]] = None
        A list of image pull secrets. This is used to authenticate with the private image registry of the images
        used by tasks.
    workflow_template_ref: Optional[str] = None
        The name of the workflowTemplate reference. WorkflowTemplateRef is a reference to a WorkflowTemplate resource.
        If you create a WorkflowTemplate resource either clusterWorkflowTemplate or not (clusterScope attribute bool)
        you can reference it again and again when you create a new Workflow without specifying the same tasks and
        dependencies. Official doc: https://argoproj.github.io/argo-workflows/fields/#workflowtemplateref
    ttl_strategy: Optional[TTLStrategy] = None
        The time to live strategy of the workflow.
    volume_claim_gc_strategy: Optional[VolumeClaimGCStrategy] = None
        Define how to delete volumes from completed Workflows.
    host_aliases: Optional[List[HostAlias]] = None
        Mappings between IP and hostnames.
    node_selectors: Optional[Dict[str, str]] = None
        A collection of key value pairs that denote node selectors. This is used for scheduling purposes. If the task
        requires GPU resources, clients are encouraged to add a node selector for a node that can satisfy the
        requested resources. In addition, clients are encouraged to specify a GPU toleration, depending on the platform
        they submit the workflow to.
    affinity: Optional[Affinity] = None
        The task affinity. This dictates the scheduling protocol of the pods running the tasks of the workflow.
    dag: Optional[DAG] = None
        The DAG to execute as part of the workflow.
    parameters: Optional[List[Parameter]] = None
        Any global parameters for the workflow.
    tolerations: Optional[List[Toleration]] = None
        List of tolerations for the pod executing the task. This is used for scheduling purposes.
    generate_name: bool = False
        Whether to use the provided name as a prefix for workflow name generation.
        If set and the workflow is created, the field `generated_name` will be populated.
    active_deadline_seconds: Optional[int] = None
        Optional duration in seconds relative to the workflow start time which the workflow
        is allowed to run.
    metrics: Optional[Union[Metric, List[Metric], Metrics]] = None
        Any built-in/custom Prometheus metrics to track.
    """

    def __init__(
        self: WorkflowType,
        name: str,
        dag_name: Optional[str] = None,
        service: Optional[WorkflowService] = None,
        parallelism: Optional[int] = None,
        service_account_name: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
        annotations: Optional[Dict[str, str]] = None,
        security_context: Optional[WorkflowSecurityContext] = None,
        image_pull_secrets: Optional[List[str]] = None,
        workflow_template_ref: Optional[str] = None,
        ttl_strategy: Optional[TTLStrategy] = None,
        volume_claim_gc_strategy: Optional[VolumeClaimGCStrategy] = None,
        host_aliases: Optional[List[HostAlias]] = None,
        node_selectors: Optional[Dict[str, str]] = None,
        affinity: Optional[Affinity] = None,
        dag: Optional[DAG] = None,
        parameters: Optional[List[Parameter]] = None,
        tolerations: Optional[List[Toleration]] = None,
        generate_name: bool = False,
        active_deadline_seconds: Optional[int] = None,
        metrics: Optional[Union[Metric, List[Metric], Metrics]] = None,
    ):
        self.name = validate_name(name)
        dag_name = self.name if dag_name is None else dag_name
        self.dag = DAG(dag_name) if dag is None else dag
        self._service = service
        self.parallelism = parallelism
        self.security_context = security_context
        self.service_account_name = (
            GlobalConfig.service_account_name if service_account_name is None else service_account_name
        )
        self.labels = labels
        self.annotations = annotations
        self.image_pull_secrets = image_pull_secrets
        self.workflow_template_ref = workflow_template_ref
        self.node_selector = node_selectors
        self.ttl_strategy = ttl_strategy
        self.affinity = affinity
        self.parameters = parameters
        self.tolerations = tolerations
        self.in_context = False
        self.volume_claim_gc_strategy = volume_claim_gc_strategy
        self.host_aliases = host_aliases
        self.generate_name = generate_name
        self.active_deadline_seconds = active_deadline_seconds
        self.exit_task: Optional[str] = None
        self.generated_name: Optional[str] = None
        self.metrics: Optional[Metrics] = None
        if metrics:
            if isinstance(metrics, Metric):
                self.metrics = Metrics([metrics])
            elif isinstance(metrics, list):
                assert all([isinstance(m, Metric) for m in metrics])
                self.metrics = Metrics(metrics)
            elif isinstance(metrics, Metrics):
                self.metrics = metrics
            else:
                raise ValueError(
                    "Unknown type provided for `metrics`, expected type is "
                    "`Optional[Union[Metric, List[Metric], Metrics]]`"
                )
        for hook in GlobalConfig.workflow_post_init_hooks:
            hook(self)

    @property
    def service(self: WorkflowType) -> WorkflowService:
        if self._service is None:
            self._service = WorkflowService()
        return self._service

    @service.setter
    def service(self: WorkflowType, value: WorkflowService):
        self._service = value

    def get_name(self: WorkflowType) -> str:
        """
        Returns the name of the workflow. This is useful in combination with
        `generate_name=True` as the name is created upon workflow creation
        """
        return "{{workflow.name}}"

    def _build_metadata(self: WorkflowType, use_name=True) -> ObjectMeta:
        """Assembles the metadata of the workflow"""
        metadata = ObjectMeta()
        if use_name:
            if self.generate_name:
                setattr(metadata, "generate_name", self.name)
            else:
                setattr(metadata, "name", self.name)
        if self.labels:
            setattr(metadata, "labels", self.labels)
        if self.annotations:
            setattr(metadata, "annotations", self.annotations)
        return metadata

    def _build_spec(self: WorkflowType) -> IoArgoprojWorkflowV1alpha1WorkflowSpec:
        """Assembles the spec of the workflow"""
        spec = IoArgoprojWorkflowV1alpha1WorkflowSpec()
        setattr(spec, "entrypoint", self.dag.name)  # This will be ignored for `WorkflowTemplate`

        templates = self.dag._build_templates() + self.dag.build()
        setattr(spec, "templates", templates)

        if self.parallelism is not None:
            setattr(spec, "parallelism", self.parallelism)

        if self.ttl_strategy is not None:
            setattr(spec, "ttl_strategy", self.ttl_strategy.build())

        if self.volume_claim_gc_strategy is not None:
            setattr(
                spec,
                "volume_claim_gc",
                IoArgoprojWorkflowV1alpha1VolumeClaimGC(strategy=self.volume_claim_gc_strategy.value),
            )

        if self.host_aliases is not None:
            setattr(spec, "host_aliases", [h.argo_host_alias for h in self.host_aliases])

        if self.security_context is not None:
            security_context = self.security_context.get_security_context()
            setattr(spec, "security_context", security_context)

        if self.service_account_name is not None:
            # setattr(main_template, "service_account_name", self.service_account_name) #TODO Is this needed?
            setattr(spec, "service_account_name", self.service_account_name)

        if self.image_pull_secrets is not None:
            secret_refs = [LocalObjectReference(name=name) for name in self.image_pull_secrets]
            setattr(spec, "image_pull_secrets", secret_refs)

        if self.parameters is not None:
            setattr(
                spec,
                "arguments",
                IoArgoprojWorkflowV1alpha1Arguments(parameters=[p.as_argument() for p in self.parameters]),
            )

        if self.affinity is not None:
            setattr(spec, "affinity", self.affinity.build())

        if self.node_selector is not None:
            setattr(spec, "node_selector", self.node_selector)

        if self.tolerations is not None:
            ts = [t.build() for t in self.tolerations]
            setattr(spec, "tolerations", ts)

        if self.active_deadline_seconds is not None:
            setattr(spec, "active_deadline_seconds", self.active_deadline_seconds)

        vct = self.dag._build_volume_claim_templates()
        if vct:
            setattr(spec, "volume_claim_templates", vct)

        pcvs = self.dag._build_persistent_volume_claims()
        if pcvs:
            setattr(spec, "volumes", pcvs)

        if self.exit_task is not None:
            setattr(spec, "on_exit", self.exit_task)

        if self.metrics is not None:
            setattr(spec, "metrics", self.metrics.build())

        return spec

    def build(self: WorkflowType) -> IoArgoprojWorkflowV1alpha1Workflow:
        """Builds the workflow core representation"""
        return IoArgoprojWorkflowV1alpha1Workflow(
            api_version=GlobalConfig.api_version,
            kind=self.__class__.__name__,
            metadata=self._build_metadata(),
            spec=self._build_spec(),
        )

    def __enter__(self: WorkflowType) -> WorkflowType:
        """Enter the context of the workflow.

        Note that this creates a DAG if one is not specified. This supports using `with Workflow(...)`.
        """
        self.in_context = True
        hera.dag_context.enter(self.dag)
        return self

    def __exit__(self: WorkflowType, exc_type, exc_val, exc_tb) -> None:
        """Leave the context of the workflow.

        This supports using `with Workflow(...)`.
        """
        self.in_context = False
        hera.dag_context.exit()

    def add_task(self: WorkflowType, t: Task) -> WorkflowType:
        """Add a task to the workflow"""
        self.dag.add_task(t)
        return self

    def add_tasks(self: WorkflowType, *ts: Task) -> WorkflowType:
        """Add a collection of tasks to the workflow"""
        self.dag.add_tasks(*ts)
        return self

    def create(self: WorkflowType) -> WorkflowType:
        """Creates the workflow"""
        if self.in_context:
            raise ValueError("Cannot invoke `create` when using a Hera context")

        resulting_argo_wf = self.service.create_workflow(self.build())
        if self.generate_name:
            self.generated_name = resulting_argo_wf.metadata.get("name")

        return self

    def lint(self: WorkflowType) -> WorkflowType:
        """Lint the workflow"""
        self.service.lint_workflow(self.build())
        return self

    def on_exit(self: WorkflowType, other: Union[Task, DAG]) -> None:
        """Add a task or a DAG to execute upon workflow exit"""
        if isinstance(other, Task):
            self.exit_task = other.name
            other.is_exit_task = True
        elif isinstance(other, DAG):
            # If the exit task is a DAG, we need to propagate the DAG and its
            # templates by instantiating a task within the current context.
            # The name will never be used; it's only present because the
            # field is mandatory.
            t = Task("temp-name-for-hera-exit-dag", dag=other)
            t.is_exit_task = True
            self.exit_task = other.name
        else:
            raise ValueError(f"Unrecognized exit type {type(other)}, supported types are `Task` and `DAG`")

    def delete(self: WorkflowType) -> Tuple[object, int, dict]:
        """Deletes the workflow"""
        return self.service.delete_workflow(self.name)

    def get_parameter(self: WorkflowType, name: str) -> Parameter:
        """Assembles the specified parameter name into a parameter specification"""
        if self.parameters is None or next((p for p in self.parameters if p.name == name), None) is None:
            raise KeyError(f"`{name}` is not a valid workflow parameter")
        return Parameter(name, value=f"{{{{workflow.parameters.{name}}}}}")

    def to_dict(self: WorkflowType, serialize: bool = True) -> dict:
        """Returns the dictionary representation of the workflow.

        Parameters
        ----------
        serialize: bool = True
            Whether to serialize extra fields from the `Workflow` model into the returned dictionary. When this is set
            to `False` extra fields, such as `node_selectors`, are not included in the returned payload.
        """
        return model_to_dict(self.build(), serialize=serialize)

    def to_json(self: WorkflowType) -> str:
        """Returns the JSON representation of the workflow"""
        return json.dumps(self.to_dict())

    def to_yaml(self: WorkflowType, **yaml_kwargs: Any) -> str:
        """Returns a YAML representation of the workflow"""
        if _yaml is None:
            raise ImportError(
                "Attempted to use `to_yaml` but PyYAML is not available. "
                "Install `hera-workflows[yaml]` to install the extra dependency"
            )
        return _yaml.dump(self.to_dict(), **yaml_kwargs)
