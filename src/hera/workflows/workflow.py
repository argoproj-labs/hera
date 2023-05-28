"""The workflow module provides the Workflow class

See https://argoproj.github.io/argo-workflows/workflow-concepts/#the-workflow
for more on Workflows.
"""
from __future__ import annotations

import time
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, List, Optional, Union

from pydantic import validator
from typing_extensions import get_args

from hera.shared import global_config
from hera.workflows._mixins import ArgumentsMixin, ContextMixin, HookMixin, MetricsMixin, VolumeMixin
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
):
    """The base Workflow class for Hera.

    Workflow implements the contextmanager interface so allows usage of `with`, under which
    any `hera.workflows.protocol.Templatable` object instantiated under the context will be
    added to the Workflow's list of templates.

    Workflows can be created directly on your Argo cluster via `create`. They can also be dumped
    to yaml via `to_yaml` or built according to the Argo schema via `build` to get an OpenAPI model
    object.
    """

    # Workflow fields - https://argoproj.github.io/argo-workflows/fields/#workflow
    api_version: Optional[str] = None
    kind: Optional[str] = None
    status: Optional[_ModelWorkflowStatus] = None

    # ObjectMeta fields - https://argoproj.github.io/argo-workflows/fields/#objectmeta
    annotations: Optional[Dict[str, str]] = None
    cluster_name: Optional[str] = None
    creation_timestamp: Optional[Time] = None
    deletion_grace_period_seconds: Optional[int] = None
    deletion_timestamp: Optional[Time] = None
    finalizers: Optional[List[str]] = None
    generate_name: Optional[str] = None
    generation: Optional[int] = None
    labels: Optional[Dict[str, str]] = None
    managed_fields: Optional[List[ManagedFieldsEntry]] = None
    name: Optional[str] = None
    namespace: Optional[str] = None
    owner_references: Optional[List[OwnerReference]] = None
    resource_version: Optional[str] = None
    self_link: Optional[str] = None
    uid: Optional[str] = None

    # WorkflowSpec fields - https://argoproj.github.io/argo-workflows/fields/#workflowspec
    active_deadline_seconds: Optional[int] = None
    affinity: Optional[Affinity] = None
    archive_logs: Optional[bool] = None
    artifact_gc: Optional[ArtifactGC] = None
    artifact_repository_ref: Optional[ArtifactRepositoryRef] = None
    automount_service_account_token: Optional[bool] = None
    dns_config: Optional[PodDNSConfig] = None
    dns_policy: Optional[str] = None
    entrypoint: Optional[str] = None
    executor: Optional[ExecutorConfig] = None
    hooks: Optional[Dict[str, LifecycleHook]] = None
    host_aliases: Optional[List[HostAlias]] = None
    host_network: Optional[bool] = None
    image_pull_secrets: ImagePullSecrets = None
    node_selector: Optional[Dict[str, str]] = None
    on_exit: Optional[Union[str, Templatable]] = None
    parallelism: Optional[int] = None
    pod_disruption_budget: Optional[PodDisruptionBudgetSpec] = None
    pod_gc: Optional[PodGC] = None
    pod_metadata: Optional[Metadata] = None
    pod_priority: Optional[int] = None
    pod_priority_class_name: Optional[str] = None
    pod_spec_patch: Optional[str] = None
    priority: Optional[int] = None
    retry_strategy: Optional[RetryStrategy] = None
    scheduler_name: Optional[str] = None
    security_context: Optional[PodSecurityContext] = None
    service_account_name: Optional[str] = None
    shutdown: Optional[str] = None
    suspend: Optional[bool] = None
    synchronization: Optional[Synchronization] = None
    template_defaults: Optional[_ModelTemplate] = None
    templates: List[Union[_ModelTemplate, Templatable]] = []
    tolerations: Optional[List[Toleration]] = None
    ttl_strategy: Optional[TTLStrategy] = None
    volume_claim_gc: Optional[VolumeClaimGC] = None
    volume_claim_templates: Optional[List[PersistentVolumeClaim]] = None
    workflow_metadata: Optional[WorkflowMetadata] = None
    workflow_template_ref: Optional[WorkflowTemplateRef] = None

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

    def _build_templates(self) -> List[TTemplate]:
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
        return templates

    def _build_on_exit(self) -> Optional[str]:
        if isinstance(self.on_exit, Templatable):
            return self.on_exit._build_template().name  # type: ignore
        return self.on_exit

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

        templates = self._build_templates()
        workflow_claims = self._build_persistent_volume_claims()
        volume_claim_templates = (self.volume_claim_templates or []) + (workflow_claims or [])
        return _ModelWorkflow(
            api_version=self.api_version,
            kind=self.kind,
            metadata=ObjectMeta(
                annotations=self.annotations,
                cluster_name=self.cluster_name,
                creation_timestamp=self.creation_timestamp,
                deletion_grace_period_seconds=self.deletion_grace_period_seconds,
                deletion_timestamp=self.deletion_timestamp,
                finalizers=self.finalizers,
                generate_name=self.generate_name,
                generation=self.generation,
                labels=self.labels,
                managed_fields=self.managed_fields,
                name=self.name,
                namespace=self.namespace,
                owner_references=self.owner_references,
                resource_version=self.resource_version,
                self_link=self.self_link,
                uid=self.uid,
            ),
            spec=_ModelWorkflowSpec(
                active_deadline_seconds=self.active_deadline_seconds,
                affinity=self.affinity,
                archive_logs=self.archive_logs,
                arguments=self._build_arguments(),
                artifact_gc=self.artifact_gc,
                artifact_repository_ref=self.artifact_repository_ref,
                automount_service_account_token=self.automount_service_account_token,
                dns_config=self.dns_config,
                dns_policy=self.dns_policy,
                entrypoint=self.entrypoint,
                executor=self.executor,
                hooks=self.hooks,
                host_aliases=self.host_aliases,
                host_network=self.host_network,
                image_pull_secrets=self.image_pull_secrets,
                metrics=self._build_metrics(),
                node_selector=self.node_selector,
                on_exit=self._build_on_exit(),
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
                template_defaults=self.template_defaults,
                templates=templates or None,
                tolerations=self.tolerations,
                ttl_strategy=self.ttl_strategy,
                volume_claim_gc=self.volume_claim_gc,
                volume_claim_templates=volume_claim_templates or None,
                volumes=self._build_volumes(),
                workflow_metadata=self.workflow_metadata,
                workflow_template_ref=self.workflow_template_ref,
            ),
            status=self.status,
        )

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


__all__ = ["Workflow"]
