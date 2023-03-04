from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from typing_extensions import get_args

from hera.shared.global_config import GlobalConfig
from hera.workflows._base_model import BaseModel
from hera.workflows.models import (
    Affinity,
    Arguments,
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
)
from hera.workflows.models import Workflow as _ModelWorkflow
from hera.workflows.models import WorkflowCreateRequest, WorkflowMetadata
from hera.workflows.models import WorkflowSpec as _ModelWorkflowSpec
from hera.workflows.models import WorkflowStatus, WorkflowTemplateRef
from hera.workflows.service import WorkflowsService
from hera.workflows.v5.exceptions import InvalidType
from hera.workflows.v5.protocol import Templatable, TTemplate


class Workflow(BaseModel):
    api_version: Optional[str] = GlobalConfig.api_version
    kind: Optional[str] = None
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
    active_deadline_seconds: Optional[int] = None
    affinity: Optional[Affinity] = None
    archive_logs: Optional[bool] = None
    arguments: Optional[Arguments] = None
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
    templates: Optional[List[TTemplate]] = None
    tolerations: Optional[List[Toleration]] = None
    ttl_strategy: Optional[TTLStrategy] = None
    volume_claim_gc: Optional[VolumeClaimGC] = None
    volume_claim_templates: Optional[List[PersistentVolumeClaim]] = None
    volumes: Optional[List[Volume]] = None
    workflow_metadata: Optional[WorkflowMetadata] = None
    workflow_template_ref: Optional[WorkflowTemplateRef] = None
    status: Optional[WorkflowStatus] = None
    workflow_service: Optional[WorkflowsService] = None

    def build(self) -> _ModelWorkflow:
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
                arguments=self.arguments,
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
                templates=self.templates,
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

    def __enter__(self) -> Workflow:
        """Enter the context of the workflow.

        Note that this creates a DAG if one is not specified. This supports using `with Workflow(...)`.
        """
        from hera.workflows.v5._context import _context

        _context.enter(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Leave the context of the workflow.

        This supports using `with Workflow(...)`.
        """
        from hera.workflows.v5._context import _context

        _context.exit()

    def create(self) -> _ModelWorkflow:
        assert self.workflow_service, "workflow service not initialized"
        assert self.namespace, "workflow service not initialized"
        return self.workflow_service.create_workflow(self.namespace, WorkflowCreateRequest(workflow=self.build()))

    def _add_sub(self, node: Any):
        self.add_template(node)

    def add_template(self, template: Union[TTemplate, Templatable]):
        self.templates = self.templates or []
        if isinstance(template, Templatable):
            self.templates.append(template._build_template())
        elif isinstance(template, get_args(TTemplate)):
            self.templates.append(template)
        else:
            raise InvalidType
