"""The cron_workflow module provides the CronWorkflow class

See https://argoproj.github.io/argo-workflows/cron-workflows
for more on CronWorkflows.
"""
from __future__ import annotations

from typing import Optional

from hera.exceptions import NotFound
from hera.workflows.models import (
    CreateCronWorkflowRequest,
    CronWorkflow as _ModelCronWorkflow,
    CronWorkflowSpec,
    CronWorkflowStatus,
    LintCronWorkflowRequest,
    ObjectMeta,
    UpdateCronWorkflowRequest,
)
from hera.workflows.protocol import TWorkflow
from hera.workflows.workflow import Workflow


class CronWorkflow(Workflow):
    """CronWorkflow allows a user to run a Workflow on a recurring basis.

    NB: Hera's CronWorkflow is a subclass of Workflow which means certain fields are renamed
    for compatibility, see `cron_suspend` and `cron_status` which are different from the Argo
    spec. See https://argoproj.github.io/argo-workflows/fields/#cronworkflow
    """

    concurrency_policy: Optional[str] = None
    failed_jobs_history_limit: Optional[int] = None
    schedule: str
    starting_deadline_seconds: Optional[int] = None
    successful_jobs_history_limit: Optional[int] = None
    cron_suspend: Optional[bool] = None
    timezone: Optional[str] = None
    cron_status: Optional[CronWorkflowStatus] = None

    def create(self) -> TWorkflow:  # type: ignore
        """Creates the CronWorkflow on the Argo cluster."""
        assert self.workflows_service, "workflow service not initialized"
        assert self.namespace, "workflow namespace not defined"
        return self.workflows_service.create_cron_workflow(
            CreateCronWorkflowRequest(cron_workflow=self.build()), namespace=self.namespace
        )

    def get(self) -> TWorkflow:
        """Attempts to get a cron workflow based on the parameters of this template e.g. name + namespace"""
        assert self.workflows_service, "workflow service not initialized"
        assert self.namespace, "workflow namespace not defined"
        assert self.name, "workflow name not defined"
        return self.workflows_service.get_cron_workflow(name=self.name, namespace=self.namespace)

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
        return self.workflows_service.update_cron_workflow(
            self.name,
            UpdateCronWorkflowRequest(template=template),
            namespace=self.namespace,
        )

    def lint(self) -> TWorkflow:
        """Lints the CronWorkflow using the Argo cluster."""
        assert self.workflows_service, "workflow service not initialized"
        assert self.namespace, "workflow namespace not defined"
        return self.workflows_service.lint_cron_workflow(
            LintCronWorkflowRequest(cron_workflow=self.build()), namespace=self.namespace
        )

    def build(self) -> TWorkflow:
        """Builds the CronWorkflow and its components into an Argo schema CronWorkflow object."""
        self = self._dispatch_hooks()

        return _ModelCronWorkflow(
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
            spec=CronWorkflowSpec(
                concurrency_policy=self.concurrency_policy,
                failed_jobs_history_limit=self.failed_jobs_history_limit,
                schedule=self.schedule,
                starting_deadline_seconds=self.starting_deadline_seconds,
                successful_jobs_history_limit=self.successful_jobs_history_limit,
                suspend=self.cron_suspend,
                timezone=self.timezone,
                workflow_metadata=None,
                workflow_spec=super().build().spec,
            ),
            status=self.cron_status,
        )


__all__ = ["CronWorkflow"]
