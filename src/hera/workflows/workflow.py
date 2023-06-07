"""The workflow module provides the Workflow class

See https://argoproj.github.io/argo-workflows/workflow-concepts/#the-workflow
for more on Workflows.
"""
from inspect import get_annotations

import time
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, List, Optional, Type, Union

try:
    from typing import Annotated, get_args, get_origin, get_type_hints
except ImportError:
    from typing_extensions import Annotated, get_args, get_origin, get_type_hints


from pydantic import BaseModel, validator

from hera.shared import global_config
from hera.workflows._mixins import (
    ArgumentsMixin,
    ContextMixin,
    HookMixin,
    MetricsMixin,
    ParseFromYamlMixin,
    VolumeMixin,
    ArgumentsT,
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

ImagePullSecrets = Optional[Union[LocalObjectReference, List[LocalObjectReference], str, List[str]]]


class Workflow(
    ArgumentsMixin,
    ContextMixin,
    HookMixin,
    VolumeMixin,
    MetricsMixin,
    ParseFromYamlMixin,
):
    """The base Workflow class for Hera.

    Workflow implements the contextmanager interface so allows usage of `with`, under which
    any `hera.workflows.protocol.Templatable` object instantiated under the context will be
    added to the Workflow's list of templates.

    Workflows can be created directly on your Argo cluster via `create`. They can also be dumped
    to yaml via `to_yaml` or built according to the Argo schema via `build` to get an OpenAPI model
    object.
    """

    class _WorkflowModelMapper(ParseFromYamlMixin.ModelMapper):
        @classmethod
        def _get_model_class(cls: "Workflow") -> Type[_ModelWorkflow]:
            return _ModelWorkflow

        # @classmethod
        # def _get_hera_class(cls: "Workflow") -> Type["Workflow"]:
        #     return Workflow

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
    # TODO: We want to pass the member directly not as a string so that validation is basically automatic
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
    image_pull_secrets: Annotated[ImagePullSecrets, _WorkflowModelMapper("spec.image_pull_secrets")] = None
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
        get_type_hints(ArgumentsMixin)["arguments"],
        _WorkflowModelMapper("spec.arguments", ArgumentsMixin._build_arguments),
    ]
    metrics: Annotated[
        get_type_hints(MetricsMixin)["metrics"], _WorkflowModelMapper("spec.metrics", MetricsMixin._build_metrics)
    ]
    volumes: Annotated[
        get_type_hints(VolumeMixin)["volumes"], _WorkflowModelMapper("spec.volumes", VolumeMixin._build_volumes)
    ]

    # Hera-specific fields
    workflows_service: Optional[WorkflowsService] = None

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

        def model_attr_setter(attrs: List[str], model_workflow: _ModelWorkflow, value: Any):
            curr: BaseModel = model_workflow
            for attr in attrs[:-1]:
                curr = getattr(curr, attr)

            setattr(curr, attrs[-1], value)

        for attr, annotation in get_annotations(Workflow).items():
            if get_origin(annotation) is Annotated and isinstance(
                get_args(annotation)[1], Workflow._WorkflowModelMapper
            ):
                mapper: Workflow._WorkflowModelMapper = get_args(annotation)[1]
                # Value comes from builder function if it exists, otherwise directly from the attr
                value = getattr(self, mapper.builder.__name__)() if mapper.builder is not None else getattr(self, attr)
                model_attr_setter(mapper.model_path, model_workflow, value)

        return model_workflow

    def to_dict(self) -> Any:
        """Builds the Workflow as an Argo schema Workflow object and returns it as a dictionary."""
        return self.build().dict(exclude_none=True, by_alias=True)

    def to_yaml(self, *args, **kwargs) -> str:
        """Builds the Workflow as an Argo schema Workflow object and returns it as yaml string."""
        if not _yaml:
            raise ImportError("PyYAML is not installed")
        # Set some default options if not provided by the user
        kwargs.setdefault("default_flow_style", False)
        kwargs.setdefault("sort_keys", False)
        return _yaml.dump(self.to_dict(), *args, **kwargs)

    def create(self, wait: bool = False, poll_interval: int = 5) -> TWorkflow:
        """Creates the Workflow on the Argo cluster.

        Parameters
        ----------
        wait: bool = False
            If true then the workflow is created asynchronously and the function returns immediately.
            If false then the workflow is created and the function blocks until the workflow is done executing.
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
        """Adds any objects instantiated under the Workflow context manager that conform to the `Templatable` protocol
        or are Argo schema Template objects to the Workflow's list of templates.
        """
        if not isinstance(node, (Templatable, _ModelTemplate)):
            raise InvalidType(type(node))
        self.templates.append(node)

    def to_file(self, output_directory: Union[Path, str] = ".", name: str = "", *args, **kwargs) -> Path:
        """Writes the Workflow as an Argo schema Workflow object to a YAML file and returns the path to the file.

        Args:
            output_directory: The directory to write the file to. Defaults to the current working directory.
            name: The name of the file to write without the file extension. Defaults to the Workflow's name or a generated name.
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
    def _from_model(cls: "Workflow", model: _ModelWorkflow) -> "Workflow":
        return Workflow(
            api_version=model.api_version,
            kind=model.kind,
            annotations=model.metadata.annotations,
            cluster_name=model.metadata.cluster_name,
            creation_timestamp=model.metadata.creation_timestamp,
            deletion_grace_period_seconds=model.metadata.deletion_grace_period_seconds,
            deletion_timestamp=model.metadata.deletion_timestamp,
            finalizers=model.metadata.finalizers,
            generate_name=model.metadata.generate_name,
            generation=model.metadata.generation,
            labels=model.metadata.labels,
            managed_fields=model.metadata.managed_fields,
            name=model.metadata.name,
            namespace=model.metadata.namespace,
            owner_references=model.metadata.owner_references,
            resource_version=model.metadata.resource_version,
            self_link=model.metadata.self_link,
            uid=model.metadata.uid,
            active_deadline_seconds=model.spec.active_deadline_seconds,
            affinity=model.spec.affinity,
            archive_logs=model.spec.archive_logs,
            arguments=model.spec.arguments,
            artifact_gc=model.spec.artifact_gc,
            artifact_repository_ref=model.spec.artifact_repository_ref,
            automount_service_account_token=model.spec.automount_service_account_token,
            dns_config=model.spec.dns_config,
            dns_policy=model.spec.dns_policy,
            entrypoint=model.spec.entrypoint,
            executor=model.spec.executor,
            hooks=model.spec.hooks,
            host_aliases=model.spec.host_aliases,
            host_network=model.spec.host_network,
            image_pull_secrets=model.spec.image_pull_secrets,
            metrics=model.spec.metrics,
            node_selector=model.spec.node_selector,
            on_exit=model.spec.on_exit,
            parallelism=model.spec.parallelism,
            pod_disruption_budget=model.spec.pod_disruption_budget,
            pod_gc=model.spec.pod_gc,
            pod_metadata=model.spec.pod_metadata,
            pod_priority=model.spec.pod_priority,
            pod_priority_class_name=model.spec.pod_priority_class_name,
            pod_spec_patch=model.spec.pod_spec_patch,
            priority=model.spec.priority,
            retry_strategy=model.spec.retry_strategy,
            scheduler_name=model.spec.scheduler_name,
            security_context=model.spec.security_context,
            service_account_name=model.spec.service_account_name,
            shutdown=model.spec.shutdown,
            suspend=model.spec.suspend,
            synchronization=model.spec.synchronization,
            template_defaults=model.spec.template_defaults,
            templates=model.spec.templates or None,
            tolerations=model.spec.tolerations,
            ttl_strategy=model.spec.ttl_strategy,
            volume_claim_gc=model.spec.volume_claim_gc,
            volume_claim_templates=model.spec.volume_claim_templates or None,
            volumes=model.spec.volumes,
            workflow_metadata=model.spec.workflow_metadata,
            workflow_template_ref=model.spec.workflow_template_ref,
            status=model.status,
        )

    @classmethod
    def from_yaml(cls: "Workflow", yaml_file: Union[Path, str]) -> "Workflow":
        """Create a Workflow from a Workflow contained in a YAML file.

        Usage:
            my_workflow = Workflow.from_yaml(yaml_file)
        """
        model_workflow = _ModelWorkflow.parse_file(yaml_file)
        return cls.from_model(model_workflow)


__all__ = ["Workflow"]
