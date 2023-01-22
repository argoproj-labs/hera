"""The implementation of a Hera cron workflow for Argo-based cron workflows"""
from enum import Enum
from typing import Optional, cast

import pytz

from hera.global_config import GlobalConfig
from hera.models import CreateCronWorkflowRequest as _ModelCreateCronWorkflowRequest
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

    @staticmethod
    def from_str(s: str) -> "ConcurrencyPolicy":
        result = {
            "allow": ConcurrencyPolicy.allow,
            "replace": ConcurrencyPolicy.replace,
            "forbid": ConcurrencyPolicy.forbid,
        }.get(s)
        assert result is not None, f"Invalid concurrency policy {s}"
        return result


class CronWorkflow(Workflow):
    def __init__(
        self: "CronWorkflow",
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
        self.suspend_ = suspend
        self.starting_deadline_seconds = starting_deadline_seconds
        self.timezone = timezone

    @staticmethod
    def from_model(m: _ModelCronWorkflow) -> "CronWorkflow":  # type: ignore
        return CronWorkflow(
            name=cast(str, m.metadata.name),
            schedule=m.spec.schedule,
            concurrency_policy=ConcurrencyPolicy.from_str(m.spec.concurrency_policy)
            if m.spec.concurrency_policy
            else None,
            failed_jobs_history_limit=m.spec.failed_jobs_history_limit,
            successful_jobs_history_limit=m.spec.successful_jobs_history_limit,
            suspend=m.spec.suspend,
            starting_deadline_seconds=m.spec.starting_deadline_seconds,
            timezone=m.spec.timezone,
            api_version=m.api_version,
            archive_logs=m.spec.workflow_spec,
        )

    def build(self: "CronWorkflow") -> _ModelCronWorkflow:  # type: ignore
        """Builds the workflow representation"""
        workflow = super().build()
        return _ModelCronWorkflow(
            api_version=GlobalConfig.api_version,
            kind=self.__class__.__name__,
            metadata=workflow.metadata,
            spec=_ModelCronWorkflowSpec(
                concurrency_policy=str(self.concurrency_policy),
                failed_jobs_history_limit=self.failed_jobs_history_limit,
                schedule=self.schedule,
                starting_deadline_seconds=self.starting_deadline_seconds,
                successful_jobs_history_limit=self.successful_jobs_history_limit,
                suspend=self.suspend_,
                timezone=self.timezone,
                workflow_metadata=self.workflow_metadata,
                workflow_spec=workflow.spec,
            ),
        )

    def create(
        self: "CronWorkflow",
        namespace: str = GlobalConfig.namespace,
        **create_kwargs,
    ) -> "CronWorkflow":
        """Creates the cron workflow"""
        if self.in_context:
            raise ValueError("Cannot invoke `create` when using a Hera context")
        return CronWorkflow.from_model(
            self.service.create_cron_workflow(
                namespace,
                _ModelCreateCronWorkflowRequest(
                    cron_workflow=self.build(),
                    namespace=namespace,
                    **create_kwargs,
                ),
            )
        )

    def lint(self: "CronWorkflow", namespace: str = GlobalConfig.namespace) -> "CronWorkflow":
        """Lint the workflow"""
        return CronWorkflow.from_model(
            self.service.lint_cron_workflow(
                namespace, _ModelLintCronWorkflowRequest(cron_workflow=self.build(), namespace=namespace)
            )
        )

    def delete(  # type: ignore
        self: "CronWorkflow",
        namespace: str = GlobalConfig.namespace,
        **delete_kwargs,
    ) -> _ModelCronWorkflowDeletedResponse:  # type: ignore
        """Deletes the cron workflow"""
        assert self.name is not None, "Cannot delete a workflow without a `name`"
        return self.service.delete_cron_workflow(
            namespace,
            self.name,
            **delete_kwargs,
        )

    def update(self: "CronWorkflow", namespace: str = GlobalConfig.namespace, **update_kwargs) -> "CronWorkflow":
        """Updates the cron workflow in the server"""
        assert self.name is not None, "Cannot update a workflow without a `name`"
        old = self.service.get_cron_workflow(namespace, self.name, **update_kwargs)
        curr = self.build()
        curr.metadata.resource_version = old.metadata.resource_version
        curr.metadata.uid = old.metadata.uid
        return CronWorkflow.from_model(
            self.service.update_cron_workflow(
                namespace, self.name, _ModelUpdateCronWorkflowRequest(cron_workflow=curr, namespace=namespace)
            )
        )

    def suspend(self: "CronWorkflow", namespace: str = GlobalConfig.namespace) -> "CronWorkflow":
        """Suspends the cron workflow"""
        assert self.name is not None, "Cannot suspend a workflow without a `name`"
        return CronWorkflow.from_model(
            self.service.suspend_cron_workflow(
                namespace, self.name, _ModelCronWorkflowSuspendRequest(name=self.name, namespace=namespace)
            )
        )

    def resume(self: "CronWorkflow", namespace: str = GlobalConfig.namespace, **resume_kwargs) -> "CronWorkflow":
        """Resumes execution of the cron workflow"""
        assert self.name is not None, "Cannot resume a workflow without a `name`"
        return CronWorkflow.from_model(
            self.service.resume_cron_workflow(
                namespace, self.name, _ModelCronWorkflowResumeRequest(name=self.name, namespace=namespace)
            )
        )

    # the following are inherited but are not actually available so reimplementing to raise an error
    def resubmit(
        self: "CronWorkflow",
        namespace: str = GlobalConfig.namespace,
        **resubmit_kwargs,
    ) -> "CronWorkflow":
        raise NotImplementedError("Not available for `CronWorkflow`")

    def retry(
        self: "CronWorkflow",
        namespace: str = GlobalConfig.namespace,
        **retry_kwargs,
    ) -> "CronWorkflow":
        raise NotImplementedError("Not available for `CronWorkflow`")

    def set(
        self: "CronWorkflow",
        namespace: str = GlobalConfig.namespace,
        **set_kwargs,
    ) -> "CronWorkflow":
        raise NotImplementedError("Not available for `CronWorkflow`")

    def stop(
        self: "CronWorkflow",
        namespace: str = GlobalConfig.namespace,
        **stop_kwargs,
    ) -> "CronWorkflow":
        raise NotImplementedError("Not available for `CronWorkflow`")

    def terminate(self: "CronWorkflow", namespace: str = GlobalConfig.namespace) -> "CronWorkflow":
        raise NotImplementedError("Not available for `CronWorkflow`")


__all__ = ["ConcurrencyPolicy", "CronWorkflow"]
