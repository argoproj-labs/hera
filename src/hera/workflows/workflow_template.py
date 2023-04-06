"""The workflow_template module provides the WorkflowTemplate class

See https://argoproj.github.io/argo-workflows/workflow-templates/
for more on WorkflowTemplates.
"""
from pydantic import validator
from typing_extensions import get_args

from hera.workflows._mixins import HookMixin
from hera.workflows.exceptions import InvalidType
from hera.workflows.models import (
    ObjectMeta,
    WorkflowSpec as _ModelWorkflowSpec,
    WorkflowTemplate as _ModelWorkflowTemplate,
    WorkflowTemplateCreateRequest,
    WorkflowTemplateLintRequest,
)
from hera.workflows.protocol import Templatable, TTemplate, TWorkflow
from hera.workflows.workflow import Workflow


class WorkflowTemplate(Workflow):
    """WorkflowTemplates are definitions of Workflows that live in your cluster. This allows you
    to create a library of frequently-used templates and reuse them by referencing them from your
    Workflows.
    """

    # WorkflowTemplate fields match Workflow exactly except for `status`, which WorkflowTemplate
    # does not have - https://argoproj.github.io/argo-workflows/fields/#workflowtemplate
    @validator("status", pre=True, always=True)
    def _set_status(cls, v):
        if v is not None:
            raise ValueError("status is not a valid field on a WorkflowTemplate")

    def create(self) -> TWorkflow:
        """Creates the WorkflowTemplate on the Argo cluster."""
        assert self.workflows_service, "workflow service not initialized"
        assert self.namespace, "workflow namespace not defined"
        return self.workflows_service.create_workflow_template(
            WorkflowTemplateCreateRequest(template=self.build()), namespace=self.namespace
        )

    def lint(self) -> TWorkflow:
        """Lints the WorkflowTemplate using the Argo cluster."""
        assert self.workflows_service, "workflow service not initialized"
        assert self.namespace, "workflow namespace not defined"
        return self.workflows_service.lint_workflow_template(
            WorkflowTemplateLintRequest(template=self.build()), namespace=self.namespace
        )

    def build(self) -> TWorkflow:
        """Builds the WorkflowTemplate and its components into an Argo schema WorkflowTemplate object."""
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

        return _ModelWorkflowTemplate(
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
        )


__all__ = ["WorkflowTemplate"]
