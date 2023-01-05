"""The implementation of a Hera workflow for Argo-based workflows"""
import json
from types import ModuleType
from typing import Any, Dict, List, Optional, Tuple, TypeVar, Union

import hera
from hera.dag import DAG
from hera.global_config import GlobalConfig
from hera.models import Affinity
from hera.models import Arguments as ModelArguments
from hera.models import (
    Artifact,
    ArtifactGC,
    ArtifactRepositoryRef,
    ExecutorConfig,
    HostAlias,
    LifecycleHook,
    LocalObjectReference,
    Metadata,
    Metrics,
    ObjectMeta,
    Parameter,
    PodDisruptionBudgetSpec,
    PodDNSConfig,
    PodGC,
    PodSecurityContext,
    Prometheus,
    RetryStrategy,
    Synchronization,
    Template,
    TTLStrategy,
    VolumeClaimGC,
)
from hera.models import Workflow as ModelWorkflow
from hera.models import WorkflowCreateRequest, WorkflowMetadata
from hera.models import WorkflowSpec as ModelWorkflowSpec
from hera.models import WorkflowTemplateRef
from hera.parameter import Parameter
from hera.service import Service
from hera.task import Task
from hera.toleration import Toleration
from hera.validators import validate_name
from hera.volumes import _BaseVolume

# PyYAML is an optional dependency
_yaml: Optional[ModuleType] = None
try:
    import yaml

    _yaml = yaml
except ImportError:
    _yaml = None

WorkflowType = TypeVar("WorkflowType", bound="Workflow")


class Workflow:
    def __init__(
        self: WorkflowType,
        name: str,
        api_version: Optional[str] = GlobalConfig.api_version,
        dag_name: Optional[str] = None,
        dag: Optional[DAG] = None,
        generate_name: bool = False,
        service: Optional[Service] = None,
        active_deadline_seconds: Optional[int] = None,
        affinity: Optional[Affinity] = None,
        acrhive_logs: Optional[bool] = None,
        inputs: Optional[
            Union[
                List[Union[Parameter, Artifact]],
                List[Union[Parameter, Artifact, Dict[str, Any]]],
                Dict[str, Any],
            ]
        ] = None,
        outputs: Optional[List[Union[Parameter, Artifact]]] = None,
        artifact_gc: Optional[ArtifactGC] = None,
        artifact_repository_ref: Optional[ArtifactRepositoryRef] = None,
        automount_service_account_token: Optional[bool] = None,
        dns_config: Optional[PodDNSConfig] = None,
        dns_policy: Optional[str] = None,
        executor: Optional[ExecutorConfig] = None,
        hooks: Optional[Dict[str, LifecycleHook]] = None,
        host_aliases: Optional[HostAlias] = Npone,
        host_network: Optional[bool] = None,
        image_pull_secrets: Optional[List[str]] = None,
        metrics: Optional[Union[Prometheus, List[Prometheus], Metrics]] = None,
        node_selector: Optional[Dict[str, str]] = None,
        parallelism: Optional[int] = None,
        pod_disruption_budget: Optional[PodDisruptionBudgetSpec] = None,
        pod_gc: Optional[PodGC] = None,
        pod_metadata: Optional[Metadata] = None,
        pod_priority: Optional[int] = None,
        pod_priority_class_name: Optional[str] = None,
        pod_spec_patch: Optional[str] = None,
        priority: Optional[int] = None,
        retry_strategy: Optional[RetryStrategy] = None,
        scheduler_name: Optional[str] = None,
        security_context: Optional[PodSecurityContext] = None,
        service_account_name: Optional[str] = GlobalConfig.service_account_name,
        shutdown: Optional[str] = None,
        suspend: Optional[bool] = None,
        synchronization: Optional[Synchronization] = None,
        template_defaults: Optional[Template] = None,
        tolerations: Optional[List[Toleration]] = None,
        ttl_strategy: Optional[TTLStrategy] = None,
        volume_claim_gc: Optional[VolumeClaimGC] = None,
        volumes: Optional[List[_BaseVolume]] = None,
        workflow_metadata: Optional[WorkflowMetadata] = None,
        workflow_template_ref: Optional[WorkflowTemplateRef] = None,
    ):
        self.name = validate_name(name, generate_name=generate_name)
        dag_name = self.name.rstrip("-.") if dag_name is None else dag_name
        self.api_version = api_version
        self.dag = DAG(dag_name) if dag is None else dag
        self.generate_name = generate_name
        self._service = service
        self.active_deadline_seconds = active_deadline_seconds
        self.affinity = affinity
        self.acrhive_logs = acrhive_logs
        self.inputs = self._parse_inputs(inputs)
        self.outputs = outputs
        self.artifact_gc = artifact_gc
        self.artifact_repository_ref = artifact_repository_ref
        self.automount_service_account_token = automount_service_account_token
        self.dns_config = dns_config
        self.dns_policy = dns_policy
        self.executor = executor
        self.hooks = hooks
        self.host_aliases = host_aliases
        self.host_network = host_network
        self.image_pull_secrets = image_pull_secrets
        self.metrics = self._parse_metrics(metrics)
        self.node_selector = node_selector
        self.parallelism = parallelism
        self.pod_disruption_budget = pod_disruption_budget
        self.pod_gc = pod_gc
        self.pod_metadata = pod_metadata
        self.pod_priority = pod_priority
        self.pod_priority_class_name = pod_priority_class_name
        self.pod_spec_patch = pod_spec_patch
        self.priority = priority
        self.retry_strategy = retry_strategy
        self.scheduler_name = scheduler_name
        self.security_context = security_context
        self.service_account_name = service_account_name
        self.shutdown = shutdown
        self.suspend = suspend
        self.synchronization = synchronization
        self.template_defaults = template_defaults
        self.tolerations = tolerations
        self.ttl_strategy = ttl_strategy
        self.volume_claim_gc = volume_claim_gc
        self.volumes = volumes
        self.workflow_metadata = workflow_metadata
        self.workflow_template_ref = workflow_template_ref

        for hook in GlobalConfig.workflow_post_init_hooks:
            hook(self)

    def _parse_metrics(self, metrics: Optional[Union[Prometheus, List[Prometheus], Metrics]]) -> Optional[Metrics]:
        if metrics is None:
            return None

        if isinstance(metrics, Prometheus):
            return Metrics(prometheus=[metrics])
        elif isinstance(metrics, list):
            assert all([isinstance(m, Prometheus) for m in metrics])
            return Metrics(prometheus=metrics)
        elif isinstance(metrics, Metrics):
            return metrics
        else:
            raise ValueError(
                "Unknown type provided for `metrics`, expected type is "
                "`Optional[Union[Metric, List[Metric], Metrics]]`"
            )

    def _parse_inputs(
        self,
        inputs: Optional[
            Union[List[Union[Parameter, Artifact]], List[Union[Parameter, Artifact, Dict[str, Any]]], Dict[str, Any]]
        ],
    ) -> List[Union[Parameter, Artifact]]:
        """Parses the dictionary aspect of the specified inputs and returns a list of parameters and artifacts.

        Parameters
        ----------
        inputs: Union[Dict[str, Any], List[Union[Parameter, Artifact, Dict[str, Any]]]]
            The list of inputs specified on the task. The `Dict` aspect is treated as a mapped collection of
            Parameters. If a single dictionary is specified, all the fields are transformed into `Parameter`s. The key
            is the `name` of the `Parameter` and the `value` is the `value` field of the `Parameter.

        Returns
        -------
        List[Union[Parameter, Artifact]]
            A list of parameters and artifacts. The parameters contain the specified dictionary mapping as well, as
            independent parameters.
        """
        if inputs is None:
            return []

        result: List[Union[Parameter, Artifact]] = []
        if isinstance(inputs, dict):
            for k, v in inputs.items():
                result.append(Parameter(name=k, value=v))
        else:
            for i in inputs:
                if isinstance(i, Parameter) or isinstance(i, Artifact):
                    result.append(i)
                elif isinstance(i, dict):
                    for k, v in i.items():
                        result.append(Parameter(name=k, value=v))
        return result

    @property
    def service(self: WorkflowType) -> Service:
        if self._service is None:
            self._service = Service()
        return self._service

    @service.setter
    def service(self: WorkflowType, value: Service):
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
                metadata.generate_name = self.name
            else:
                metadata.name = self.name
        return metadata

    def _build_spec(self: WorkflowType) -> ModelWorkflowSpec:
        """Assembles the spec of the workflow"""
        return ModelWorkflowSpec(
            active_deadline_seconds=self.active_deadline_seconds,
            affinity=self.affinity,
            archive_logs=self.acrhive_logs,
            arguments=ModelArguments(
                artifacts=[a for a in self.inputs if isinstance(a, Artifact)],
                parameters=[p for p in self.inputs if isinstance(p, Parameter)],
            ),
            artifact_gc=self.artifact_gc,
            automount_service_account_token=self.automount_service_account_token,
            dns_config=self.dns_config,
            dns_policy=self.dns_policy,
            entrypoint=self.dag.name,
            executor=self.executor,
            hooks=self.hooks,
            host_aliases=self.host_aliases,
            host_network=self.host_networks,
            image_pull_secrets=[LocalObjectReference(name=name) for name in self.image_pull_secrets],
            metrics=self.metrics,
            node_selector=self.node_selector,
            on_exit=self.exit_task,
            parallelism=self.parallelism,
            pod_disruption_budget=self.pod_disruption_budget,
            pod_gc=self.pod_gc,
            pod_metadata=self.pod_metadata,
            pod_priority=self.pod_priority,
            pod_priority_class_name=self.pod_priority_class_name,
            pod_spec_patch=self.pod_spec_patch,
            priority=self.priority,
            retry_strategy=self.retry_strategy,
            scheduler_name=self.scheduler_name,
            security_context=self.security_context,
            service_account_name=self.service_account_name,
            shutdown=self.shutdown,
            suspend=self.suspend,
            synchronization=self.synchronization,
            templates=self.dag._build_templates() + self.dag.build(),
            template_defaults=self.template_defaults,
            tolerations=self.tolerations,
            ttl_strategy=self.ttl_strategy,
            volume_claim_gc=self.volume_claim_gc,
            volume_claim_templates=self.dag._build_volume_claim_templates(),
            volumes=self.dag._build_persistent_volume_claims(),
            workflow_metadata=self.workflow_metadata,
            workflow_template_ref=self.workflow_template_ref,
        )

    def build(self: WorkflowType) -> ModelWorkflow:
        """Builds the workflow core representation"""
        return ModelWorkflow(
            api_version=self.api_version,
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
        return Parameter(name=name, value=f"{{{{workflow.parameters.{name}}}}}")

    def to_dict(self: WorkflowType) -> dict:
        """Returns the dictionary representation of the workflow"""
        return self.build().dict(exclude_none=True, by_alias=True)

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
        return self.build().to_yaml(**yaml_kwargs)
