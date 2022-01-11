"""The implementation of a Hera workflow for Argo-based workflows"""
from typing import Optional
from uuid import uuid4

from argo.workflows.client import (
    V1alpha1DAGTemplate,
    V1alpha1Template,
    V1alpha1Workflow,
    V1alpha1WorkflowSpec,
    V1ObjectMeta,
)

from hera.task import Task
from hera.workflow_service import WorkflowService


class Workflow:
    """A workflow representation.

    The workflow is used as a functional representation for a collection of tasks and
    steps. The workflow context controls the overall behaviour of tasks, such as whether to notify completion, whether
    to execute retires, overall parallelism, etc. The workflow can be constructed and submitted to multiple Argo
    endpoints as long as a token can be associated with the endpoint at the given domain.

    Parameters
    ----------
    name: str
        The workflow name. Note that the workflow initiation will replace underscores with dashes.
    service: WorkflowService
        A workflow service to use for submissions. See `hera.v1.workflow_service.WorkflowService`.
    parallelism: int = 50
        The number of parallel tasks to run in case a task group is executed for multiple tasks.
    service_account_name: Optional[str] = None
        The name of the service account to use in all workflow tasks.
    """

    def __init__(
        self, name: str, service: WorkflowService, parallelism: int = 50, service_account_name: Optional[str] = None
    ):
        self.name = f'{name.replace("_", "-")}-{str(uuid4()).split("-")[0]}'  # RFC1123
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
        self.workflow = V1alpha1Workflow(metadata=self.metadata, spec=self.spec)

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

    def submit(self, namespace: str = 'default') -> None:
        """Submits the workflow"""
        self.service.submit(self.workflow, namespace)
