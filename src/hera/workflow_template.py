"""The implementation of a Hera workflowTemplate for Argo-based workflowTemplates"""
from typing import Dict, Optional

from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1DAGTemplate,
    IoArgoprojWorkflowV1alpha1Template,
    IoArgoprojWorkflowV1alpha1WorkflowTemplate,
    IoArgoprojWorkflowV1alpha1WorkflowTemplateSpec,
    ObjectMeta,
)

from hera.security_context import WorkflowSecurityContext
from hera.task import Task
from hera.ttl_strategy import TTLStrategy
from hera.workflow_editors import add_head, add_tail, add_task, add_tasks
from hera.workflow_template_service import WorkflowTemplateService


class WorkflowTemplate:
    """A workflowTemplate representation.

    The WorkflowTemplate is used as a functional representation for a collection of tasks and
    steps. The WorkflowTemplate is basically the same as a Workflow but with a template you don't
    have to write the same steps, you can reuse it over and over.

    Parameters
    ----------
    name: str
        The workflowTemplate name. Note that the workflowTemplate initiation will replace underscores with dashes.
    service: WorkflowService
        A workflowTemplate service to use for submissions.
        See `hera.v1.workflow_template_service.WorkflowTemplateService`.
    parallelism: int = 50
        The number of parallel tasks to run in case a task group is executed for multiple tasks.
    service_account_name: Optional[str] = None
        The name of the service account to use in all workflow tasks.
    security_context:  Optional[WorkflowSecurityContext] = None
        Define security settings for all containers in the workflow.
    labels: Optional[Dict[str, str]] = None
        A Dict of labels to attach to the Workflow object metadata
    namespace: Optional[str] = 'default'
        The namespace to use for creating the WorkflowTemplate.  Defaults to "default"
    """

    def __init__(
        self,
        name: str,
        service: WorkflowTemplateService,
        parallelism: int = 50,
        service_account_name: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
        namespace: Optional[str] = None,
        security_context: Optional[WorkflowSecurityContext] = None,
        ttl_strategy: Optional[TTLStrategy] = None,
    ):
        self.name = f'{name.replace("_", "-")}'  # RFC1123
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

        self.spec = IoArgoprojWorkflowV1alpha1WorkflowTemplateSpec(
            templates=[self.template], entrypoint=self.name, volumes=[], volume_claim_templates=[]
        )

        if ttl_strategy:
            setattr(self.spec, 'ttl_strategy', ttl_strategy.argo_ttl_strategy)

        if self.security_context:
            security_context = self.security_context.get_security_context()
            setattr(self.spec, 'security_context', security_context)

        if self.service_account_name:
            setattr(self.template, 'service_account_name', self.service_account_name)
            setattr(self.spec, 'service_account_name', self.service_account_name)

        self.metadata = ObjectMeta(name=self.name)
        if self.labels:
            setattr(self.metadata, 'labels', self.labels)

        self.workflow_template = IoArgoprojWorkflowV1alpha1WorkflowTemplate(metadata=self.metadata, spec=self.spec)

    def add_task(self, t: Task) -> None:
        add_task(self, t)

    def add_tasks(self, *ts: Task) -> None:
        add_tasks(self, *ts)

    def add_head(self, t: Task, append: bool = True) -> None:
        add_head(self, t, append=append)

    def add_tail(self, t: Task, append: bool = True) -> None:
        add_tail(self, t, append=append)

    def create(self, namespace: Optional[str] = None) -> IoArgoprojWorkflowV1alpha1WorkflowTemplate:
        """Creates the workflow"""
        if namespace is None:
            namespace = self.namespace
        return self.service.create(self.workflow_template, namespace)
