"""The implementation of a Hera cron workflow for Argo-based cron workflows"""

from typing import Optional

from argo.workflows.client import (
    V1alpha1CronWorkflow,
    V1alpha1CronWorkflowSpec,
)
from hera.v1.cron_workflow_service import CronWorkflowService
from hera.v1.workflow_service import WorkflowService
from hera.v1.workflow import Workflow


class CronWorkflow(Workflow):
    """A cron workflow representation.

    CronWorkflow are workflows that run on a preset schedule.
    In essence, CronWorkflow = Workflow + some specific cron options.

    Parameters
    ----------
    name: str
        The cron workflow name. Note that the cron workflow initiation will replace underscores with dashes.
    service: WorkflowService
        A workflow service to use for submissions. See `hera.v1.workflow_service.WorkflowService`.
    schedule: str
        Schedule at which the Workflow will be run in Cron format. E.g. 5 4 * * *
    parallelism: int = 50
        The number of parallel tasks to run in case a task group is executed for multiple tasks.
    """

    def __init__(
        self,
        name: str,
        schedule: str,
        service: WorkflowService,
        cron_service: CronWorkflowService,
        parallelism: int = 50,
    ):
        super().__init__(name, service, parallelism)
        self.schedule = schedule

        self.cron_workflow_spec = V1alpha1CronWorkflowSpec(schedule=self.schedule, workflow_spec=self.spec)
        self.cron_workflow = V1alpha1CronWorkflow(metadata=self.metadata, spec=self.cron_workflow_spec)
        self.cron_service = cron_service

    def suspend(self, name: str, namespace: Optional[str] = None):
        """Suspends the cron workflow"""
        self.cron_service.suspend(name, namespace)

    def resume(self, name: str, namespace: Optional[str] = None):
        """Resumes execution of the cron workflow"""
        self.cron_service.resume(name, namespace)

    def submit(self, namespace: Optional[str] = None) -> None:
        self.cron_service.submit(self.cron_workflow, namespace)
