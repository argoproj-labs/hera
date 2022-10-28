"""The implementation of a Hera cron workflow for Argo-based cron workflows"""
from enum import Enum
from typing import Optional, Tuple

import pytz
from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1CronWorkflow,
    IoArgoprojWorkflowV1alpha1CronWorkflowSpec,
)

from hera.host_config import get_global_api_version
from hera.workflow import Workflow


class ConcurrencyPolicy(str, Enum):
    """Specifies how to treat concurrent executions of a job that is created by a cron workflow.

    Notes
    -----
    See https://kubernetes.io/docs/tasks/job/automated-tasks-with-cron-jobs/#concurrency-policy
    """

    Allow = "Allow"
    """Default, cron job allows concurrently running jobs"""

    Replace = "Replace"
    """
    If it is time for a new job run and the previous job run hasn't finished yet, the cron job replaces the
    currently running job run with a new job run
    """

    Forbid = "Forbid"
    """
    The cron job does not allow concurrent runs; if it is time for a new job run and the previous job run hasn't
    finished yet, the cron job skips the new job run.
    """

    def __str__(self):
        return str(self.value)


class CronWorkflow(Workflow):
    """A cron workflow representation.

    CronWorkflow are workflows that run on a preset schedule.
    In essence, CronWorkflow = Workflow + some specific cron options.

    See https://argoproj.github.io/argo-workflows/cron-workflows/

    Parameters
    ----------
    name: str
        Name of the workflow.
    schedule: str
        Schedule at which the Workflow will be run in Cron format e.g. 5 4 * * *.
    concurrency_policy: Optional[ConcurrencyPolicy] = None
        Concurrency policy that dictates the concurrency behavior of multiple cron jobs of the same kind.
        See `hera.cron_workflow.ConcurrencyPolicy`
    starting_deadline_seconds: Optional[int] = None
        The number of seconds the workflow has as a starting deadline.
    timezone: Optional[str] = None
        Timezone during which the Workflow will be run from the IANA timezone standard, e.g. America/Los_Angeles.
    **kwargs
        Any kwargs to set on the workflow. See `hera.workflow.Workflow`.
    """

    def __init__(
        self,
        name: str,
        schedule: str,
        concurrency_policy: Optional[ConcurrencyPolicy] = None,
        starting_deadline_seconds: Optional[int] = None,
        timezone: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(name, **kwargs)
        if timezone and timezone not in pytz.all_timezones:
            raise ValueError(f"{timezone} is not a valid timezone")
        self.schedule = schedule
        self.timezone = timezone
        self.starting_deadline_seconds = starting_deadline_seconds
        self.concurrency_policy = concurrency_policy

    def build(self) -> IoArgoprojWorkflowV1alpha1CronWorkflow:
        """Builds the workflow representation"""
        workflow = super().build()
        cron_workflow_spec = IoArgoprojWorkflowV1alpha1CronWorkflowSpec(
            schedule=self.schedule,
            workflow_spec=workflow.spec,
            workflow_metadata=super()._build_metadata(use_name=False),
        )
        if self.concurrency_policy:
            setattr(cron_workflow_spec, "concurrencyPolicy", self.concurrency_policy.value)
        if self.starting_deadline_seconds:
            setattr(cron_workflow_spec, "startingDeadlineSeconds", self.starting_deadline_seconds)
        if self.timezone:
            setattr(cron_workflow_spec, "timezone", self.timezone)

        return IoArgoprojWorkflowV1alpha1CronWorkflow(
            api_version=get_global_api_version(),
            kind=self.__class__.__name__,
            metadata=workflow.metadata,
            spec=cron_workflow_spec,
        )

    def create(self) -> "CronWorkflow":
        """Creates the cron workflow"""
        if self.in_context:
            raise ValueError("Cannot invoke `create` when using a Hera context")
        self.service.create_cron_workflow(self.build())
        return self

    def lint(self) -> "CronWorkflow":
        """Lint the workflow"""
        self.service.lint_cron_workflow(self.build())
        return self

    def delete(self) -> Tuple[object, int, dict]:
        """Deletes the cron workflow"""
        return self.service.delete_cron_workflow(self.name)

    def update(self) -> "CronWorkflow":
        """Updates the cron workflow in the server"""

        # when update cron_workflow, metadata.resourceVersion and metadata.uid should be same as the previous value
        old_workflow = self.service.get_cron_workflow(self.name)
        cron_workflow = self.build()
        cron_workflow.metadata["resourceVersion"] = old_workflow.metadata["resourceVersion"]
        cron_workflow.metadata["uid"] = old_workflow.metadata["uid"]
        self.service.update_cron_workflow(self.name, cron_workflow)
        return self

    def suspend(self) -> Tuple[object, int, dict]:
        """Suspends the cron workflow"""
        return self.service.suspend_cron_workflow(self.name)

    def resume(self) -> Tuple[object, int, dict]:
        """Resumes execution of the cron workflow"""
        return self.service.resume_cron_workflow(self.name)
