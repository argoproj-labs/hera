"""The workflow module provides the Workflow class

See https://argoproj.github.io/argo-workflows/workflow-concepts/#the-workflow
for more on Workflows.
"""
from __future__ import annotations

from types import ModuleType
from typing import Any, Dict, List, Optional, Union

from pydantic import validator
from typing_extensions import get_args

from hera.shared import global_config
from hera.workflows._mixins import ArgumentsMixin, ContextMixin, HookMixin
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
    Metrics,
    ObjectMeta,
    OwnerReference,
    PersistentVolumeClaim,
    PodDisruptionBudgetSpec,
    PodDNSConfig,
    PodGC,
    PodSecurityContext,
    RetryStrategy,
    Synchronization,
    Template,
    Time,
    Toleration,
    TTLStrategy,
    Volume,
    VolumeClaimGC,
    Workflow as _ModelWorkflow,
    WorkflowCreateRequest,
    WorkflowLintRequest,
    WorkflowMetadata,
    WorkflowSpec as _ModelWorkflowSpec,
    WorkflowStatus,
    WorkflowTemplateRef,
)
from hera.workflows.protocol import Templatable, TTemplate, TWorkflow, VolumeClaimable
from hera.workflows.service import WorkflowsService

_yaml: Optional[ModuleType] = None
try:
    import yaml

    _yaml = yaml
except ImportError:
    _yaml = None


class Workflow(
    ArgumentsMixin,
    ContextMixin,
    HookMixin,
):
    """The base Workflow class for Hera.

    Workflow implements the contextmanager interface so allows usage of `with`, under which
    any `hera.workflows.protocol.Templatable` object or `hera.workflows.models.Template` object
    instantiated under the context will be added to the Workflow's list of templates.

    Workflows can be created directly on your Argo cluster via `create`. They can also be dumped
    to yaml via `to_yaml` or built according to the Argo schema via `build` to get an OpenAPI model
    object.
    """

    # Workflow fields - https://argoproj.github.io/argo-workflows/fields/#workflow
    api_version: Optional[str] = global_config.api_version
    kind: Optional[str] = None
    status: Optional[WorkflowStatus] = None

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
    image_pull_secrets: Optional[List[LocalObjectReference]] = None
    metrics: Optional[Metrics] = None
    node_selector: Optional[Dict[str, str]] = None
    on_exit: Optional[str] = None
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
    template_defaults: Optional[Template] = None
    templates: List[Union[Template, Templatable]] = []
    tolerations: Optional[List[Toleration]] = None
    ttl_strategy: Optional[TTLStrategy] = None
    volume_claim_gc: Optional[VolumeClaimGC] = None
    volume_claim_templates: Optional[List[PersistentVolumeClaim]] = None
    volumes: Optional[List[Volume]] = None
    workflow_metadata: Optional[WorkflowMetadata] = None
    workflow_template_ref: Optional[WorkflowTemplateRef] = None

    # Hera-specific fields
    workflows_service: Optional[WorkflowsService] = None

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

    def build(self) -> TWorkflow:
        """Builds the Workflow and its components into an Argo schema Workflow object."""
        self = self._dispatch_hooks()

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
                metrics=self.metrics,
                node_selector=self.node_selector,
                on_exit=self.on_exit,
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
                volume_claim_templates=self.volume_claim_templates,
                volumes=self.volumes,
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
        return _yaml.dump(self.to_dict(), *args, **kwargs)

    def create(self) -> TWorkflow:
        """Creates the Workflow on the Argo cluster."""
        assert self.workflows_service, "workflow service not initialized"
        assert self.namespace, "workflow namespace not defined"
        return self.workflows_service.create_workflow(self.namespace, WorkflowCreateRequest(workflow=self.build()))

    def lint(self) -> TWorkflow:
        """Lints the Workflow using the Argo cluster."""
        assert self.workflows_service, "workflow service not initialized"
        assert self.namespace, "workflow namespace not defined"
        return self.workflows_service.lint_workflow(self.namespace, WorkflowLintRequest(workflow=self.build()))

    def _add_sub(self, node: Any):
        """Adds any objects instantiated under the Workflow context manager that conform to the `Templatable` protocol
        or are Argo schema Template objects to the Workflow's list of templates.
        """
        if not isinstance(node, (Templatable, *get_args(Template))):
            raise InvalidType(type(node))
        self.templates.append(node)


__all__ = ["Workflow"]
