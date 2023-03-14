from __future__ import annotations

from typing import Dict, List, Optional, Union

from typing_extensions import get_args

from hera.workflows._mixins import ArgumentsMixin
from hera.workflows.artifact import Artifact
from hera.workflows.exceptions import InvalidType
from hera.workflows.models import (
    Affinity,
    Artifact as _ModelArtifact,
    ArtifactGC,
    ArtifactRepositoryRef,
    ExecutorConfig,
    HostAlias,
    LifecycleHook,
    LocalObjectReference,
    Metadata,
    Metrics,
    Parameter as _ModelParameter,
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
    WorkflowMetadata,
    WorkflowSpec as _ModelWorkflowSpec,
    WorkflowTemplateRef,
)
from hera.workflows.parameter import Parameter
from hera.workflows.protocol import Templatable, TTemplate


class WorkflowSpec(ArgumentsMixin):
    active_deadline_seconds: Optional[int] = None
    affinity: Optional[Affinity] = None
    archive_logs: Optional[bool] = None
    arguments: Optional[List[Union[Artifact, _ModelArtifact, Parameter, _ModelParameter]]] = None
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

    def build(self) -> _ModelWorkflowSpec:
        templates = []
        for template in self.templates:
            if isinstance(template, Templatable):
                templates.append(template._build_template())
            elif isinstance(template, get_args(TTemplate)):
                templates.append(template)
            else:
                raise InvalidType(f"{type(template)} is not a valid template type")

        return _ModelWorkflowSpec(
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
        )
