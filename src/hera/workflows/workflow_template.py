"""The workflow_template module provides the WorkflowTemplate class

See https://argoproj.github.io/argo-workflows/workflow-templates/
for more on WorkflowTemplates.
"""
from pydantic import validator

from hera.exceptions import NotFound
from hera.workflows.models import (
    ObjectMeta,
    WorkflowSpec as _ModelWorkflowSpec,
    WorkflowTemplate as _ModelWorkflowTemplate,
    WorkflowTemplateCreateRequest,
    WorkflowTemplateLintRequest,
    WorkflowTemplateUpdateRequest,
)
from hera.workflows.protocol import TWorkflow
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

    def create(self) -> TWorkflow:  # type: ignore
        """Creates the WorkflowTemplate on the Argo cluster."""
        assert self.workflows_service, "workflow service not initialized"
        assert self.namespace, "workflow namespace not defined"
        return self.workflows_service.create_workflow_template(
            WorkflowTemplateCreateRequest(template=self.build()), namespace=self.namespace
        )

    def get(self) -> TWorkflow:
        """Attempts to get a workflow template based on the parameters of this template e.g. name + namespace"""
        assert self.workflows_service, "workflow service not initialized"
        assert self.namespace, "workflow namespace not defined"
        assert self.name, "workflow name not defined"
        return self.workflows_service.get_workflow_template(name=self.name, namespace=self.namespace)

    def update(self) -> TWorkflow:
        """
        Attempts to perform a workflow template update based on the parameters of this template
        e.g. name, namespace. Note that this creates the template if it does not exist. In addition, this performs
        a get prior to updating to get the resource version to update in the first place. If you know the template
        does not exist ahead of time, it is more efficient to use `create()` directly to avoid one round trip.
        """
        assert self.workflows_service, "workflow service not initialized"
        assert self.namespace, "workflow namespace not defined"
        assert self.name, "workflow name not defined"
        # we always need to do a get prior to updating to get the resource version to update in the first place
        # https://github.com/argoproj/argo-workflows/pull/5465#discussion_r597797052

        template = self.build()
        try:
            curr = self.get()
            template.metadata.resource_version = curr.metadata.resource_version
        except NotFound:
            return self.create()
        return self.workflows_service.update_workflow_template(
            self.name,
            WorkflowTemplateUpdateRequest(template=template),
            namespace=self.namespace,
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

        templates = self._build_templates()
        workflow_claims = self._build_persistent_volume_claims()
        volume_claim_templates = (self.volume_claim_templates or []) + (workflow_claims or [])
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
        )


__all__ = ["WorkflowTemplate"]
