"""The implementation of a Hera cron workflow for Argo-based cron workflows"""
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from argo.workflows.client import (
    V1alpha1CronWorkflow,
    V1alpha1CronWorkflowSpec,
    V1alpha1CronWorkflowStatus,
    V1alpha1DAGTemplate,
    V1alpha1Template,
    V1alpha1WorkflowSpec,
    V1ObjectMeta,
)

from hera.cron_workflow_service import CronWorkflowService
from hera.task import Task


class CronWorkflow:
    """A cron workflow representation.

    CronWorkflow are workflows that run on a preset schedule.
    In essence, CronWorkflow = Workflow + some specific cron options.

    Parameters
    ----------
    name: str
        The cron workflow name. Note that the cron workflow initiation will replace underscores with dashes.
    service: CronWorkflowService
        A cron workflow service to use for creations. See `hera.v1.cron_workflow_service.CronWorkflowService`.
    schedule: str
        Schedule at which the Workflow will be run in Cron format. E.g. 5 4 * * *
    parallelism: int = 50
        The number of parallel tasks to run in case a task group is executed for multiple tasks.
    service_account_name: Optional[str] = None
        The name of the service account to use in all workflow tasks.
    """

    def __init__(
        self,
        name: str,
        schedule: str,
        service: CronWorkflowService,
        parallelism: int = 50,
        service_account_name: Optional[str] = None,
    ):
        self.name = f'{name.replace("_", "-")}-{str(uuid4()).split("-")[0]}'
        self.schedule = schedule
        self.service = service
        self.parallelism = parallelism
        self.service_account_name = service_account_name

        self.dag_template = V1alpha1DAGTemplate(tasks=[])
        self.template = V1alpha1Template(
            name=self.name,
            steps=[],
            dag=self.dag_template,
            parallelism=self.parallelism,
            service_account_name=self.service_account_name,
        )
        self.metadata = V1ObjectMeta(name=self.name)
        self.spec = V1alpha1WorkflowSpec(
            templates=[self.template], entrypoint=self.name, service_account_name=self.service_account_name
        )

        self.cron_spec = V1alpha1CronWorkflowSpec(schedule=self.schedule, workflow_spec=self.spec)
        self.workflow = V1alpha1CronWorkflow(
            metadata=self.metadata,
            spec=self.cron_spec,
            status=V1alpha1CronWorkflowStatus(
                active=[], conditions=[], last_scheduled_time=datetime.now(timezone.utc)
            ),
        )

    def add_task(self, t: Task) -> None:
        """Adds a single task to the workflow"""
        self.add_tasks(t)

    def add_tasks(self, *ts: Task) -> None:
        """Adds multiple tasks to the workflow"""
        if not all(ts):
            return
        if not self.spec.volume_claim_templates:
            self.spec.volume_claim_templates = []
        for t in ts:
            self.spec.templates.append(t.argo_template)

            if t.resources.volume:
                if not self.spec.volume_claim_templates:
                    self.spec.volume_claim_templates = [t.resources.volume.get_claim_spec()]
                else:
                    self.spec.volume_claim_templates.append(t.resources.volume.get_claim_spec())

            if t.resources.existing_volume:
                if not self.spec.volumes:
                    self.spec.volumes = [t.resources.existing_volume.get_volume()]
                else:
                    self.spec.volumes.append(t.resources.existing_volume.get_volume())

            if t.resources.empty_dir_volume:
                if not self.spec.volumes:
                    self.spec.volumes = [t.resources.empty_dir_volume.get_volume()]
                else:
                    self.spec.volumes.append(t.resources.empty_dir_volume.get_volume())

            self.dag_template.tasks.append(t.argo_task)

    def add_head(self, t: Task, append: bool = True) -> None:
        """Adds a task at the head of the workflow so the workflow start with the given task.

        This sets the given task as a dependency of the starting tasks of the workflow.

        Parameters
        ----------
        t: Task
            The task to add to the head of the workflow.
        append: bool = True
            Whether to append the given task to the workflow.
        """
        if append:
            self.add_task(t)

        for template_task in self.dag_template.tasks:
            if template_task.name != t.name:
                if template_task.dependencies:
                    template_task.dependencies.append(t.name)
                else:
                    template_task.dependencies = [t.name]

    def add_tail(self, t: Task, append: bool = True) -> None:
        """Adds a task as the tail of the workflow so the workflow ends with the given task.

        This sets the given task's dependencies to all the tasks that are not listed as dependencies in the workflow.

        Parameters
        ----------
        t: Task
            The task to add to the tail of the workflow.
        append: bool = True
            Whether to append the given task to the workflow.
        """
        if append:
            self.add_task(t)

        dependencies = set()
        task_name_to_task = dict()
        for template_task in self.dag_template.tasks:
            if template_task.dependencies:
                dependencies.update(template_task.dependencies)
            if template_task.name != t.name:
                task_name_to_task[template_task.name] = template_task

        # the tasks that are not listed as dependencies are "end tasks" i.e nothing follows after
        # e.g if A -> B -> C then B.deps = [A] and C.deps = [B] but nothing lists C so C is "free"
        free_tasks = set(task_name_to_task.keys()).difference(dependencies)
        t.argo_task.dependencies = list(free_tasks)

    def create(self, namespace: str = 'default') -> None:
        """Creates the cron workflow in the server"""
        self.service.create(self.workflow, namespace)

    def suspend(self, name: str, namespace: str = 'default'):
        """Suspends the cron workflow"""
        self.service.suspend(name, namespace)

    def resume(self, name: str, namespace: str = 'default'):
        """Resumes execution of the cron workflow"""
        self.service.resume(name, namespace)
