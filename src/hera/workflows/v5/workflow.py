from __future__ import annotations

from typing import Dict, List, Optional, TypeVar

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
    Metadata,
    Metrics,
    ObjectMeta,
    PersistentVolumeClaim,
    PodDisruptionBudgetSpec,
    PodDNSConfig,
    PodGC,
    PodSecurityContext,
    RetryStrategy,
    Synchronization,
    Template,
    Toleration,
    TTLStrategy,
    Volume,
    VolumeClaimGC,
)
from hera.workflows.models import Workflow as _ModelWorkflow
from hera.workflows.models import WorkflowMetadata
from hera.workflows.models import WorkflowSpec as _ModelWorkflowSpec
from hera.workflows.models import WorkflowStatus, WorkflowTemplateRef
from hera.workflows.service import WorkflowsService


class Workflow(BaseModel):
    api_version: Optional[str] = GlobalConfig.api_version
    kind: Optional[str] = None
    metadata: Optional[ObjectMeta] = None
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
    templates: Optional[List[Template]] = None
    tolerations: Optional[List[Toleration]] = None
    ttl_strategy: Optional[TTLStrategy] = None
    volume_claim_gc: Optional[VolumeClaimGC] = None
    volume_claim_templates: Optional[List[PersistentVolumeClaim]] = None
    volumes: Optional[List[Volume]] = None
    workflow_metadata: Optional[WorkflowMetadata] = None
    workflow_template_ref: Optional[WorkflowTemplateRef] = None
    status: Optional[WorkflowStatus] = None
    workflow_service: Optional[WorkflowsService] = None

    _in_context: bool = False

    @property
    def name(self) -> str:
        return "{{workflow.name}}"

    def build(self) -> _ModelWorkflow:
        return _ModelWorkflow(
            api_version=self.api_version,
            kind=self.kind,
            metadata=self.metadata,
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
        self._in_context = True
        # hera.workflows.dag_context.enter(self.dag)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Leave the context of the workflow.

        This supports using `with Workflow(...)`.
        """
        self._in_context = False
        # hera.workflows.dag_context.exit()
