"""The workflow module provides the Workflow class.

See https://argoproj.github.io/argo-workflows/workflow-concepts/#the-workflow
for more on Workflows.
"""
import time
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, List, Optional, Type, Union

try:
    from typing import Annotated, get_args  # type: ignore
except ImportError:
    from typing_extensions import Annotated, get_args  # type: ignore


from pydantic import validator

from hera.shared import global_config
from hera.shared._base_model import BaseModel
from hera.workflows._mixins import (
    ArgumentsMixin,
    ArgumentsT,
    ContextMixin,
    HookMixin,
    MetricsMixin,
    MetricsT,
    ModelMapperMixin,
    VolumeMixin,
    VolumesT,
)
from hera.workflows.exceptions import InvalidType
from hera.workflows.models import (
    Affinity,
    ArtifactGC,
    ArtifactRepositoryRef,
    ExecutorConfig,
    HostAlias,
    LifecycleHook,
    LocalObjectReference,
    ManagedFieldsEntry,
    Metadata,
    ObjectMeta,
    OwnerReference,
    PersistentVolumeClaim,
    PodDisruptionBudgetSpec,
    PodDNSConfig,
    PodGC,
    PodSecurityContext,
    RetryStrategy,
    Synchronization,
    Template as _ModelTemplate,
    Time,
    Toleration,
    TTLStrategy,
    VolumeClaimGC,
    Workflow as _ModelWorkflow,
    WorkflowCreateRequest,
    WorkflowLintRequest,
    WorkflowMetadata,
    WorkflowSpec as _ModelWorkflowSpec,
    WorkflowStatus as _ModelWorkflowStatus,
    WorkflowTemplateRef,
)
from hera.workflows.parameter import Parameter
from hera.workflows.protocol import Templatable, TTemplate, TWorkflow, VolumeClaimable
from hera.workflows.service import WorkflowsService
from hera.workflows.workflow_status import WorkflowStatus

_yaml: Optional[ModuleType] = None
try:
    import yaml

    _yaml = yaml
except ImportError:
    _yaml = None

ImagePullSecretsT = Optional[Union[LocalObjectReference, List[LocalObjectReference], str, List[str]]]

NAME_LIMIT = 63

# The length of the random suffix used for generate_name
# length (5) from https://github.com/kubernetes/kubernetes/blob/6195f96e/staging/src/k8s.io/apiserver/pkg/storage/names/generate.go#L45
_SUFFIX_LEN = 5
# The max name length comes from https://github.com/kubernetes/kubernetes/blob/6195f96e/staging/src/k8s.io/apiserver/pkg/storage/names/generate.go#L44
# We want to truncate according to SUFFIX_LEN
_TRUNCATE_LENGTH = NAME_LIMIT - _SUFFIX_LEN


class _WorkflowModelMapper(ModelMapperMixin.ModelMapper):
    @classmethod
    def _get_model_class(cls) -> Type[BaseModel]:
        return _ModelWorkflow


class Workflow(
    ArgumentsMixin,
    ContextMixin,
    HookMixin,
    VolumeMixin,
    MetricsMixin,
    ModelMapperMixin,
):
    """The base Workflow class for Hera.

    Workflow implements the contextmanager interface so allows usage of `with`, under which
    any `hera.workflows.protocol.Templatable` object instantiated under the context will be
    added to the Workflow's list of templates.

    Workflows can be created directly on your Argo cluster via `create`. They can also be dumped
    to yaml via `to_yaml` or built according to the Argo schema via `build` to get an OpenAPI model
    object.
    """

    def _build_volume_claim_templates(self) -> Optional[List]:
        return ((self.volume_claim_templates or []) + (self._build_persistent_volume_claims() or [])) or None

    def _build_on_exit(self) -> Optional[str]:
        if isinstance(self.on_exit, Templatable):
            return self.on_exit._build_template().name  # type: ignore
        return self.on_exit

    def _build_templates(self) -> Optional[List[TTemplate]]:
        """Builds the templates into an Argo schema."""
        templates = []
        for template in self.templates:
            if isinstance(template, HookMixin):
                template = template._dispatch_hooks()

            if isinstance(template, Templatable):
                templates.append(template._build_template())
            elif isinstance(template, get_args(TTemplate)):
                templates.append(template)
            else:
                raise InvalidType(f"{type(template)} is not a valid template type")

            if isinstance(template, VolumeClaimable):
                claims = template._build_persistent_volume_claims()
                # If there are no claims, continue, nothing to add
                if not claims:
                    continue
                # If there are no volume claim templates, set them to the constructed claims
                elif self.volume_claim_templates is None:
                    self.volume_claim_templates = claims
                else:
                    # otherwise, we need to merge the two lists of volume claim templates. This prioritizes the
                    # already existing volume claim templates under the assumption that the user has already set
                    # a claim template on the workflow intentionally, or the user is sharing the same volumes across
                    # different templates
                    current_volume_claims_map = {}
                    for claim in self.volume_claim_templates:
                        assert claim.metadata is not None, "expected a workflow volume claim with metadata"
                        assert claim.metadata.name is not None, "expected a named workflow volume claim"
                        current_volume_claims_map[claim.metadata.name] = claim

                    new_volume_claims_map = {}
                    for claim in claims:
                        assert claim.metadata is not None, "expected a volume claim with metadata"
                        assert claim.metadata.name is not None, "expected a named volume claim"
                        new_volume_claims_map[claim.metadata.name] = claim

                    for claim_name, claim in new_volume_claims_map.items():
                        if claim_name not in current_volume_claims_map:
                            self.volume_claim_templates.append(claim)
        return templates or None

    # Workflow fields - https://argoproj.github.io/argo-workflows/fields/#workflow
    api_version: Annotated[Optional[str], _WorkflowModelMapper("api_version")] = None
    kind: Annotated[Optional[str], _WorkflowModelMapper("kind")] = None
    status: Annotated[Optional[_ModelWorkflowStatus], _WorkflowModelMapper("status")] = None

    # ObjectMeta fields - https://argoproj.github.io/argo-workflows/fields/#objectmeta
    annotations: Annotated[Optional[Dict[str, str]], _WorkflowModelMapper("metadata.annotations")] = None
    cluster_name: Annotated[Optional[str], _WorkflowModelMapper("metadata.cluster_name")] = None
    creation_timestamp: Annotated[Optional[Time], _WorkflowModelMapper("metadata.creation_timestamp")] = None
    deletion_grace_period_seconds: Annotated[
        Optional[int], _WorkflowModelMapper("metadata.deletion_grace_period_seconds")
    ] = None
    deletion_timestamp: Annotated[Optional[Time], _WorkflowModelMapper("metadata.deletion_timestamp")] = None
    finalizers: Annotated[Optional[List[str]], _WorkflowModelMapper("metadata.finalizers")] = None
    generate_name: Annotated[Optional[str], _WorkflowModelMapper("metadata.generate_name")] = None
    generation: Annotated[Optional[int], _WorkflowModelMapper("metadata.generation")] = None
    labels: Annotated[Optional[Dict[str, str]], _WorkflowModelMapper("metadata.labels")] = None
    managed_fields: Annotated[
        Optional[List[ManagedFieldsEntry]], _WorkflowModelMapper("metadata.managed_fields")
    ] = None
    name: Annotated[Optional[str], _WorkflowModelMapper("metadata.name")] = None
    namespace: Annotated[Optional[str], _WorkflowModelMapper("metadata.namespace")] = None
    owner_references: Annotated[
        Optional[List[OwnerReference]], _WorkflowModelMapper("metadata.owner_references")
    ] = None
    resource_version: Annotated[Optional[str], _WorkflowModelMapper("metadata.resource_version")] = None
    self_link: Annotated[Optional[str], _WorkflowModelMapper("metadata.self_link")] = None
    uid: Annotated[Optional[str], _WorkflowModelMapper("metadata.uid")] = None

    # WorkflowSpec fields - https://argoproj.github.io/argo-workflows/fields/#workflowspec
    active_deadline_seconds: Annotated[Optional[int], _WorkflowModelMapper("spec.active_deadline_seconds")] = None
    affinity: Annotated[Optional[Affinity], _WorkflowModelMapper("spec.affinity")] = None
    archive_logs: Annotated[Optional[bool], _WorkflowModelMapper("spec.archive_logs")] = None
    artifact_gc: Annotated[Optional[ArtifactGC], _WorkflowModelMapper("spec.artifact_gc")] = None
    artifact_repository_ref: Annotated[
        Optional[ArtifactRepositoryRef], _WorkflowModelMapper("spec.artifact_repository_ref")
    ] = None
    automount_service_account_token: Annotated[
        Optional[bool], _WorkflowModelMapper("spec.automount_service_account_token")
    ] = None
    dns_config: Annotated[Optional[PodDNSConfig], _WorkflowModelMapper("spec.dns_config")] = None
    dns_policy: Annotated[Optional[str], _WorkflowModelMapper("spec.dns_policy")] = None
    entrypoint: Annotated[Optional[str], _WorkflowModelMapper("spec.entrypoint")] = None
    executor: Annotated[Optional[ExecutorConfig], _WorkflowModelMapper("spec.executor")] = None
    hooks: Annotated[Optional[Dict[str, LifecycleHook]], _WorkflowModelMapper("spec.hooks")] = None
    host_aliases: Annotated[Optional[List[HostAlias]], _WorkflowModelMapper("spec.host_aliases")] = None
    host_network: Annotated[Optional[bool], _WorkflowModelMapper("spec.host_network")] = None
    image_pull_secrets: Annotated[ImagePullSecretsT, _WorkflowModelMapper("spec.image_pull_secrets")] = None
    node_selector: Annotated[Optional[Dict[str, str]], _WorkflowModelMapper("spec.node_selector")] = None
    on_exit: Annotated[Optional[Union[str, Templatable]], _WorkflowModelMapper("spec.on_exit", _build_on_exit)] = None
    parallelism: Annotated[Optional[int], _WorkflowModelMapper("spec.parallelism")] = None
    pod_disruption_budget: Annotated[
        Optional[PodDisruptionBudgetSpec], _WorkflowModelMapper("spec.pod_disruption_budget")
    ] = None
    pod_gc: Annotated[Optional[PodGC], _WorkflowModelMapper("spec.pod_gc")] = None
    pod_metadata: Annotated[Optional[Metadata], _WorkflowModelMapper("spec.pod_metadata")] = None
    pod_priority: Annotated[Optional[int], _WorkflowModelMapper("spec.pod_priority")] = None
    pod_priority_class_name: Annotated[Optional[str], _WorkflowModelMapper("spec.pod_priority_class_name")] = None
    pod_spec_patch: Annotated[Optional[str], _WorkflowModelMapper("spec.pod_spec_patch")] = None
    priority: Annotated[Optional[int], _WorkflowModelMapper("spec.priority")] = None
    retry_strategy: Annotated[Optional[RetryStrategy], _WorkflowModelMapper("spec.retry_strategy")] = None
    scheduler_name: Annotated[Optional[str], _WorkflowModelMapper("spec.scheduler_name")] = None
    security_context: Annotated[Optional[PodSecurityContext], _WorkflowModelMapper("spec.security_context")] = None
    service_account_name: Annotated[Optional[str], _WorkflowModelMapper("spec.service_account_name")] = None
    shutdown: Annotated[Optional[str], _WorkflowModelMapper("spec.shutdown")] = None
    suspend: Annotated[Optional[bool], _WorkflowModelMapper("spec.suspend")] = None
    synchronization: Annotated[Optional[Synchronization], _WorkflowModelMapper("spec.synchronization")] = None
    template_defaults: Annotated[Optional[_ModelTemplate], _WorkflowModelMapper("spec.template_defaults")] = None
    templates: Annotated[
        List[Union[_ModelTemplate, Templatable]], _WorkflowModelMapper("spec.templates", _build_templates)
    ] = []
    tolerations: Annotated[Optional[List[Toleration]], _WorkflowModelMapper("spec.tolerations")] = None
    ttl_strategy: Annotated[Optional[TTLStrategy], _WorkflowModelMapper("spec.ttl_strategy")] = None
    volume_claim_gc: Annotated[Optional[VolumeClaimGC], _WorkflowModelMapper("spec.volume_claim_gc")] = None
    volume_claim_templates: Annotated[
        Optional[List[PersistentVolumeClaim]],
        _WorkflowModelMapper("spec.volume_claim_templates", _build_volume_claim_templates),
    ] = None
    workflow_metadata: Annotated[Optional[WorkflowMetadata], _WorkflowModelMapper("spec.workflow_metadata")] = None
    workflow_template_ref: Annotated[
        Optional[WorkflowTemplateRef], _WorkflowModelMapper("spec.workflow_template_ref")
    ] = None

    # Override types for mixin fields
    arguments: Annotated[
        ArgumentsT,
        _WorkflowModelMapper("spec.arguments", ArgumentsMixin._build_arguments),
    ]
    metrics: Annotated[
        MetricsT,
        _WorkflowModelMapper("spec.metrics", MetricsMixin._build_metrics),
    ]
    volumes: Annotated[VolumesT, _WorkflowModelMapper("spec.volumes", VolumeMixin._build_volumes)]

    # Hera-specific fields
    workflows_service: Optional[WorkflowsService] = None

    @validator("name", pre=True, always=True)
    def _set_name(cls, v):
        if v is not None and len(v) > NAME_LIMIT:
            raise ValueError(f"name must be no more than {NAME_LIMIT} characters: {v}")
        return v

    @validator("generate_name", pre=True, always=True)
    def _set_generate_name(cls, v):
        if v is not None and len(v) > NAME_LIMIT:
            raise ValueError(f"generate_name must be no more than {NAME_LIMIT} characters: {v}")
        return v

    @validator("api_version", pre=True, always=True)
    def _set_api_version(cls, v):
        if v is None:
            return global_config.api_version
        return v

    @validator("workflows_service", pre=True, always=True)
    def _set_workflows_service(cls, v):
        if v is None:
            return WorkflowsService()
        return v

    @validator("kind", pre=True, always=True)
    def _set_kind(cls, v):
        if v is None:
            return cls.__name__  # type: ignore
        return v

    @validator("namespace", pre=True, always=True)
    def _set_namespace(cls, v):
        if v is None:
            return global_config.namespace
        return v

    @validator("service_account_name", pre=True, always=True)
    def _set_service_account_name(cls, v):
        if v is None:
            return global_config.service_account_name
        return v

    @validator("image_pull_secrets", pre=True, always=True)
    def _set_image_pull_secrets(cls, v):
        if v is None:
            return None

        if isinstance(v, str):
            return [LocalObjectReference(name=v)]
        elif isinstance(v, LocalObjectReference):
            return [v]

        assert isinstance(v, list), (
            "`image_pull_secrets` expected to be either a `str`, a `LocalObjectReferences`, a list of `str`, "
            "or a list of `LocalObjectReferences`"
        )
        result = []
        for secret in v:
            if isinstance(secret, str):
                result.append(LocalObjectReference(name=secret))
            elif isinstance(secret, LocalObjectReference):
                result.append(secret)
        return result

    def get_parameter(self, name: str) -> Parameter:
        """Attempts to find and return a `Parameter` of the specified name."""
        arguments = self._build_arguments()
        if arguments is None:
            raise KeyError("Workflow has no arguments set")
        if arguments.parameters is None:
            raise KeyError("Workflow has no argument parameters set")

        parameters = arguments.parameters
        if next((p for p in parameters if p.name == name), None) is None:
            raise KeyError(f"`{name}` is not a valid workflow parameter")
        return Parameter(name=name, value=f"{{{{workflow.parameters.{name}}}}}")

    def build(self) -> TWorkflow:
        """Builds the Workflow and its components into an Argo schema Workflow object."""
        self = self._dispatch_hooks()

        model_workflow = _ModelWorkflow(
            metadata=ObjectMeta(),
            spec=_ModelWorkflowSpec(),
        )
        return _WorkflowModelMapper.build_model(Workflow, self, model_workflow)

    def to_dict(self) -> Any:
        """Builds the Workflow as an Argo schema Workflow object and returns it as a dictionary."""
        return self.build().dict(exclude_none=True, by_alias=True)

    def __eq__(self, other) -> bool:
        """Verifies equality of `self` with the specified `other`."""
        if other.__class__ is self.__class__:
            return self.to_dict() == other.to_dict()

        return False

    def to_yaml(self, *args, **kwargs) -> str:
        """Builds the Workflow as an Argo schema Workflow object and returns it as yaml string."""
        if not _yaml:
            raise ImportError("`PyYAML` is not installed. Install `hera[yaml]` to bring in the extra dependency")
        # Set some default options if not provided by the user
        kwargs.setdefault("default_flow_style", False)
        kwargs.setdefault("sort_keys", False)
        return _yaml.dump(self.to_dict(), *args, **kwargs)

    def create(self, wait: bool = False, poll_interval: int = 5) -> TWorkflow:
        """Creates the Workflow on the Argo cluster.

        Parameters
        ----------
        wait: bool = False
            If false then the workflow is created asynchronously and the function returns immediately.
            If true then the workflow is created and the function blocks until the workflow is done executing.
        poll_interval: int = 5
            The interval in seconds to poll the workflow status if wait is true. Ignored when wait is true.
        """
        assert self.workflows_service, "workflow service not initialized"
        assert self.namespace, "workflow namespace not defined"

        wf = self.workflows_service.create_workflow(
            WorkflowCreateRequest(workflow=self.build()), namespace=self.namespace
        )
        # set the workflow name to the name returned by the API, which helps cover the case of users relying on
        # `generate_name=True`
        self.name = wf.metadata.name

        if wait:
            return self.wait(poll_interval=poll_interval)
        return wf

    def wait(self, poll_interval: int = 5) -> TWorkflow:
        """Waits for the Workflow to complete execution.

        Parameters
        ----------
        poll_interval: int = 5
            The interval in seconds to poll the workflow status.
        """
        assert self.workflows_service is not None, "workflow service not initialized"
        assert self.namespace is not None, "workflow namespace not defined"
        assert self.name is not None, "workflow name not defined"

        wf = self.workflows_service.get_workflow(self.name, namespace=self.namespace)
        assert wf.metadata.name is not None, f"workflow name not defined for workflow {self.name}"

        assert wf.status is not None, f"workflow status not defined for workflow {wf.metadata.name}"
        assert wf.status.phase is not None, f"workflow phase not defined for workflow status {wf.status}"
        status = WorkflowStatus.from_argo_status(wf.status.phase)

        # keep polling for workflow status until completed, at the interval dictated by the user
        while status == WorkflowStatus.running:
            time.sleep(poll_interval)
            wf = self.workflows_service.get_workflow(wf.metadata.name, namespace=self.namespace)
            assert wf.status is not None, f"workflow status not defined for workflow {wf.metadata.name}"
            assert wf.status.phase is not None, f"workflow phase not defined for workflow status {wf.status}"
            status = WorkflowStatus.from_argo_status(wf.status.phase)
        return wf

    def lint(self) -> TWorkflow:
        """Lints the Workflow using the Argo cluster."""
        assert self.workflows_service, "workflow service not initialized"
        assert self.namespace, "workflow namespace not defined"
        return self.workflows_service.lint_workflow(
            WorkflowLintRequest(workflow=self.build()), namespace=self.namespace
        )

    def _add_sub(self, node: Any):
        """Adds the given node (expected to satisfy the `Templatable` protocol) to the context."""
        if not isinstance(node, (Templatable, _ModelTemplate)):
            raise InvalidType(type(node))
        self.templates.append(node)

    def to_file(self, output_directory: Union[Path, str] = ".", name: str = "", *args, **kwargs) -> Path:
        """Writes the Workflow as an Argo schema Workflow object to a YAML file and returns the path to the file.

        Args:
            output_directory: The directory to write the file to. Defaults to the current working directory.
            name: The name of the file to write without the file extension.  Defaults to the Workflow's name or a
            generated name.
            *args: Additional arguments to pass to `yaml.dump`.
            **kwargs: Additional keyword arguments to pass to `yaml.dump`.
        """
        workflow_name = self.name or (self.generate_name or "workflow").rstrip("-")
        name = name or workflow_name
        output_directory = Path(output_directory)
        output_path = Path(output_directory) / f"{name}.yaml"
        output_directory.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self.to_yaml(*args, **kwargs))
        return output_path.absolute()

    @classmethod
    def from_dict(cls, model_dict: Dict) -> ModelMapperMixin:
        """Create a Workflow from a Workflow contained in a dict.

        Examples:
            my_workflow = Workflow(...)
            my_workflow == Workflow.from_dict(my_workflow.to_dict())
        """
        return cls._from_dict(model_dict, _ModelWorkflow)

    @classmethod
    def from_yaml(cls, yaml_str: str) -> ModelMapperMixin:
        """Create a Workflow from a Workflow contained in a YAML string.

        Usage:
            my_workflow = Workflow.from_yaml(yaml_str)
        """
        return cls._from_yaml(yaml_str, _ModelWorkflow)

    @classmethod
    def from_file(cls, yaml_file: Union[Path, str]) -> ModelMapperMixin:
        """Create a Workflow from a Workflow contained in a YAML file.

        Usage:
            yaml_file = Path(...)
            my_workflow = Workflow.from_file(yaml_file)
        """
        return cls._from_file(yaml_file, _ModelWorkflow)


__all__ = ["Workflow"]
