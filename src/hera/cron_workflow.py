"""The implementation of a Hera cron workflow for Argo-based cron workflows"""
from enum import Enum
from typing import List, Optional

import pytz

from hera.global_config import GlobalConfig
from hera.models import CreateCronWorkflowRequest as _ModelCreateCronWorkflowRequest
from hera.models import CreateOptions
from hera.models import CronWorkflow as _ModelCronWorkflow
from hera.models import CronWorkflowDeletedResponse as _ModelCronWorkflowDeletedResponse
from hera.models import CronWorkflowResumeRequest as _ModelCronWorkflowResumeRequest
from hera.models import CronWorkflowSpec as _ModelCronWorkflowSpec
from hera.models import CronWorkflowSuspendRequest as _ModelCronWorkflowSuspendRequest
from hera.models import LintCronWorkflowRequest as _ModelLintCronWorkflowRequest
from hera.models import UpdateCronWorkflowRequest as _ModelUpdateCronWorkflowRequest
from hera.workflow import Workflow


class ConcurrencyPolicy(Enum):
    """Specifies how to treat concurrent executions of a job that is created by a cron workflow.

    Notes
    -----
    See https://kubernetes.io/docs/tasks/job/automated-tasks-with-cron-jobs/#concurrency-policy
    """

    allow = "Allow"
    """Default, cron job allows concurrently running jobs"""

    replace = "Replace"
    """
    If it is time for a new job run and the previous job run hasn't finished yet, the cron job replaces the
    currently running job run with a new job run
    """

    forbid = "Forbid"
    """
    The cron job does not allow concurrent runs; if it is time for a new job run and the previous job run hasn't
    finished yet, the cron job skips the new job run.
    """

    def __str__(self):
        return str(self.value)


class CronWorkflow(Workflow):
    def __init__(
        self,
        name: str,
        schedule: str,
        concurrency_policy: Optional[ConcurrencyPolicy] = None,
        failed_jobs_history_limit: Optional[int] = None,
        successful_jobs_history_limit: Optional[int] = None,
        suspend: Optional[bool] = None,
        starting_deadline_seconds: Optional[int] = None,
        timezone: Optional[str] = None,
        **workflow_kwargs,
    ):
        super().__init__(name, **workflow_kwargs)
        if timezone and timezone not in pytz.all_timezones:
            raise ValueError(f"{timezone} is not a valid timezone")
        self.schedule = schedule
        self.concurrency_policy = concurrency_policy
        self.failed_jobs_history_limit = failed_jobs_history_limit
        self.successful_jobs_history_limit = successful_jobs_history_limit
        self.suspend = suspend
        self.starting_deadline_seconds = starting_deadline_seconds
        self.timezone = timezone

    def build(self) -> _ModelCronWorkflow:
        """Builds the workflow representation"""
        workflow = super().build()
        return _ModelCronWorkflow(
            api_version=self.api_version,
            kind=self.__class__.__name__,
            metadata=workflow.metadata,
            spec=_ModelCronWorkflowSpec(
                concurrency_policy=str(self.concurrency_policy),
                failed_jobs_history_limit=self.failed_jobs_history_limit,
                schedule=self.schedule,
                starting_deadline_seconds=self.starting_deadline_seconds,
                successful_jobs_history_limit=self.successful_jobs_history_limit,
                suspend=self.suspend,
                timezone=self.timezone,
                workflow_metadata=self.workflow_metadata,
                workflow_spec=workflow.spec,
            ),
        )

    def create(
        self, namespace: str = GlobalConfig.namespace, create_options: Optional[CreateOptions] = None
    ) -> "CronWorkflow":
        """Creates the cron workflow"""
        if self.in_context:
            raise ValueError("Cannot invoke `create` when using a Hera context")
        return self.service.create_cron_workflow(
            namespace,
            _ModelCreateCronWorkflowRequest(
                create_options=create_options,
                cron_workflow=self.build(),
                namespace=namespace,
            ),
        )

    def lint(self, namespace: Optional[str] = GlobalConfig.namespace) -> "CronWorkflow":
        """Lint the workflow"""
        return self.service.lint_cron_workflow(
            namespace, _ModelLintCronWorkflowRequest(cron_workflow=self.build(), namespace=namespace)
        )

    def delete(
        self,
        name: str,
        namespace: str = GlobalConfig.namespace,
        grace_period_seconds: Optional[str] = None,
        uid: Optional[str] = None,
        resource_version: Optional[str] = None,
        orphan_dependents: Optional[bool] = None,
        propagation_policy: Optional[str] = None,
        dry_run: Optional[list] = None,
    ) -> _ModelCronWorkflowDeletedResponse:
        """Deletes the cron workflow"""
        return self.service.delete_cron_workflow(
            namespace,
            name,
            grace_period_seconds=grace_period_seconds,
            uid=uid,
            resource_version=resource_version,
            orphan_dependents=orphan_dependents,
            propagation_policy=propagation_policy,
            dry_run=dry_run,
        )

    def update(
        self, namespace: str = GlobalConfig.namespace, resource_version: Optional[str] = None
    ) -> "CronWorkflow":
        """Updates the cron workflow in the server"""
        old = self.service.get_cron_workflow(namespace, self.name, resource_version=resource_version)
        curr = self.build()
        curr.metadata.resource_version = old.metadata.resource_version
        curr.metadata.uid = old.metadata.uid
        return self.service.update_cron_workflow(
            namespace, self.name, _ModelUpdateCronWorkflowRequest(cron_workflow=curr, namespace=namespace)
        )

    def suspend(self, namespace: str = GlobalConfig.namespace) -> "CronWorkflow":
        """Suspends the cron workflow"""
        return self.service.suspend_cron_workflow(
            namespace, self.name, _ModelCronWorkflowSuspendRequest(name=self.name, namespace=namespace)
        )

    def resume(self, namespace: str = GlobalConfig.namespace) -> "CronWorkflow":
        """Resumes execution of the cron workflow"""
        return self.service.resume_cron_workflow(
            namespace, self.name, _ModelCronWorkflowResumeRequest(name=self.name, namespace=namespace)
        )

    # the following are inherited but are not actually available so reimplementing to raise an error
    def resubmit(
        self: "CronWorkflow",
        namespace: str = GlobalConfig.namespace,
        memoized: Optional[bool] = None,
        parameters: Optional[List[str]] = None,
    ) -> "CronWorkflow":
        raise NotImplementedError("Not available for `CronWorkflow`")

    def retry(
        self: "CronWorkflow",
        namespace: str = GlobalConfig.namespace,
        node_field_selector: Optional[List[str]] = None,
        parameters: Optional[List[str]] = None,
        restart_successful: Optional[bool] = None,
    ) -> "CronWorkflow":
        raise NotImplementedError("Not available for `CronWorkflow`")

    def set(
        self: "CronWorkflow",
        namespace: GlobalConfig.namespace,
        message: Optional[str] = None,
        node_field_selector: Optional[str] = None,
        output_parameters: Optional[str] = None,
        phase: Optional[str] = None,
    ) -> "CronWorkflow":
        raise NotImplementedError("Not available for `CronWorkflow`")

    def stop(
        self,
        namespace: str = GlobalConfig.namespace,
        message: Optional[str] = None,
        node_field_selector: Optional[str] = None,
    ) -> "CronWorkflow":
        raise NotImplementedError("Not available for `CronWorkflow`")

    def terminate(self, namespace: str = GlobalConfig.namespace) -> "CronWorkflow":
        raise NotImplementedError("Not available for `CronWorkflow`")


__all__ = ["ConcurrencyPolicy", "CronWorkflow"]
