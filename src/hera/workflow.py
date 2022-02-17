"""The implementation of a Hera workflow for Argo-based workflows"""
from typing import Dict, Optional
from uuid import uuid4

from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1DAGTemplate,
    IoArgoprojWorkflowV1alpha1Template,
    IoArgoprojWorkflowV1alpha1Workflow,
    IoArgoprojWorkflowV1alpha1WorkflowSpec,
    ObjectMeta,
)

from hera.security_context import WorkflowSecurityContext
from hera.task import Task
from hera.volumes import Volume
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
    security_context:  Optional[WorkflowSecurityContext] = None
        Define security settings for all containers in the workflow.
    labels: Optional[Dict[str, str]] = None
        A Dict of labels to attach to the Workflow object metadata
    namespace: Optional[str] = 'default'
        The namespace to use for creating the Workflow.  Defaults to "default"
    """

    def __init__(
        self,
        name: str,
        service: WorkflowService,
        parallelism: int = 50,
        service_account_name: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
        namespace: Optional[str] = None,
        security_context: Optional[WorkflowSecurityContext] = None,
    ):
        self.name = f'{name.replace("_", "-")}-{str(uuid4()).split("-")[0]}'  # RFC1123
        self.namespace = namespace or 'default'
        self.service = service
        self.parallelism = parallelism
        self.security_context = security_context
        self.service_account_name = service_account_name
        self.labels = labels

        self.dag_template = IoArgoprojWorkflowV1alpha1DAGTemplate(tasks=[])
        self.template = IoArgoprojWorkflowV1alpha1Template(
            name=self.name,
            steps=[],
            dag=self.dag_template,
            parallelism=self.parallelism,
        )

        self.spec = IoArgoprojWorkflowV1alpha1WorkflowSpec(
            templates=[self.template], entrypoint=self.name, volumes=[], volume_claim_templates=[]
        )
        if self.security_context:
            security_context = self.security_context.get_security_context()
            setattr(self.spec, 'security_context', security_context)

        if self.service_account_name:
            setattr(self.template, 'service_account_name', self.service_account_name)
            setattr(self.spec, 'service_account_name', self.service_account_name)

        self.metadata = ObjectMeta(name=self.name)
        if self.labels:
            setattr(self.metadata, 'labels', self.labels)

        self.workflow = IoArgoprojWorkflowV1alpha1Workflow(metadata=self.metadata, spec=self.spec)

    def add_task(self, t: Task) -> None:
        """Adds a single task to the workflow"""
        self.add_tasks(t)

    def add_tasks(self, *ts: Task) -> None:
        """Adds multiple tasks to the workflow"""
        if not all(ts):
            return

        for t in ts:
            self.spec.templates.append(t.argo_template)

            if t.resources.volumes:
                for vol in t.resources.volumes:
                    if isinstance(vol, Volume):
                        # dynamically provisioned volumes need associated claims on the workflow spec
                        self.spec.volume_claim_templates.append(vol.get_claim_spec())
                    else:
                        self.spec.volumes.append(vol.get_volume())

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
                if hasattr(template_task, 'dependencies'):
                    template_task.dependencies.append(t.name)
                else:
                    setattr(template_task, 'dependencies', [t.name])

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
            if hasattr(template_task, 'dependencies'):
                dependencies.update(template_task.dependencies)
            if template_task.name != t.name:
                task_name_to_task[template_task.name] = template_task

        # the tasks that are not listed as dependencies are "end tasks" i.e nothing follows after
        # e.g if A -> B -> C then B.deps = [A] and C.deps = [B] but nothing lists C so C is "free"
        free_tasks = set(task_name_to_task.keys()).difference(dependencies)
        t.argo_task.dependencies = list(free_tasks)

    def submit(self, namespace: Optional[str] = None) -> IoArgoprojWorkflowV1alpha1Workflow:
        """Submits the workflow"""
        if namespace is None:
            namespace = self.namespace
        return self.service.submit(self.workflow, namespace)
