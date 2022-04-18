"""The implementation of a Hera workflow for Argo-based workflows"""
from typing import Dict, List, Optional, Tuple

from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1DAGTemplate,
    IoArgoprojWorkflowV1alpha1Template,
    IoArgoprojWorkflowV1alpha1Workflow,
    IoArgoprojWorkflowV1alpha1WorkflowSpec,
    IoArgoprojWorkflowV1alpha1WorkflowTemplateRef,
    LocalObjectReference,
    ObjectMeta,
)

from hera.security_context import WorkflowSecurityContext
from hera.task import Task
from hera.ttl_strategy import TTLStrategy
from hera.workflow_editors import add_head, add_tail, add_task, add_tasks
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
    labels: Optional[Dict[str, str]] = None
        A Dict of labels to attach to the Workflow object metadata
    annotations: Optional[Dict[str, str]] = None
        A Dict of annotations to attach to the Workflow object metadata
    namespace: Optional[str] = 'default'
        The namespace to use for creating the Workflow.  Defaults to "default"
    security_context:  Optional[WorkflowSecurityContext] = None
        Define security settings for all containers in the workflow.
    image_pull_secrets: Optional[List[str]] = None
        A list of image pull secrets. This is used to authenticate with the private image registry of the images
        used by tasks.
    workflow_template_ref: Optional[str] = None
        The name of the workflowTemplate reference. WorkflowTemplateRef is a reference to a WorkflowTemplate resource.
        If you create a WorkflowTemplate resource either clusterWorkflowTemplate or not (clusterScope attribute bool)
        you can reference it again and again when you create a new Workflow without specifying the same tasks and
        dependencies. Official doc: https://argoproj.github.io/argo-workflows/fields/#workflowtemplateref
    """

    def __init__(
        self,
        name: str,
        service: WorkflowService,
        parallelism: int = 50,
        service_account_name: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
        annotations: Optional[Dict[str, str]] = None,
        namespace: Optional[str] = None,
        security_context: Optional[WorkflowSecurityContext] = None,
        image_pull_secrets: Optional[List[str]] = None,
        workflow_template_ref: Optional[str] = None,
        ttl_strategy: Optional[TTLStrategy] = None,
    ):
        self.name = f'{name.replace("_", "-")}'  # RFC1123
        self.namespace = namespace or 'default'
        self.service = service
        self.parallelism = parallelism
        self.security_context = security_context
        self.service_account_name = service_account_name
        self.labels = labels
        self.annotations = annotations
        self.image_pull_secrets = image_pull_secrets
        self.workflow_template_ref = workflow_template_ref

        self.dag_template = IoArgoprojWorkflowV1alpha1DAGTemplate(tasks=[])
        self.template = IoArgoprojWorkflowV1alpha1Template(
            name=self.name,
            steps=[],
            dag=self.dag_template,
            parallelism=self.parallelism,
        )

        if self.workflow_template_ref:
            self.workflow_template = IoArgoprojWorkflowV1alpha1WorkflowTemplateRef(name=self.workflow_template_ref)
            self.spec = IoArgoprojWorkflowV1alpha1WorkflowSpec(
                workflow_template_ref=self.workflow_template,
                entrypoint=self.workflow_template_ref,
                volumes=[],
                volume_claim_templates=[],
            )
        else:
            self.spec = IoArgoprojWorkflowV1alpha1WorkflowSpec(
                templates=[self.template],
                entrypoint=self.name,
                volumes=[],
                volume_claim_templates=[],
            )

        if ttl_strategy:
            setattr(self.spec, 'ttl_strategy', ttl_strategy.argo_ttl_strategy)

        if self.security_context:
            security_context = self.security_context.get_security_context()
            setattr(self.spec, 'security_context', security_context)

        if self.service_account_name:
            setattr(self.template, 'service_account_name', self.service_account_name)
            setattr(self.spec, 'service_account_name', self.service_account_name)

        if self.image_pull_secrets:
            secret_refs = [LocalObjectReference(name=name) for name in self.image_pull_secrets]
            setattr(self.spec, 'image_pull_secrets', secret_refs)

        self.metadata = ObjectMeta(name=self.name)
        if self.labels:
            setattr(self.metadata, 'labels', self.labels)
        if self.annotations:
            setattr(self.metadata, 'annotations', self.annotations)

        self.workflow = IoArgoprojWorkflowV1alpha1Workflow(metadata=self.metadata, spec=self.spec)

    def add_task(self, t: Task) -> None:
        add_task(self, t)

    def add_tasks(self, *ts: Task) -> None:
        add_tasks(self, *ts)

    def add_head(self, t: Task, append: bool = True) -> None:
        add_head(self, t, append=append)

    def add_tail(self, t: Task, append: bool = True) -> None:
        add_tail(self, t, append=append)

    def create(self, namespace: Optional[str] = None) -> IoArgoprojWorkflowV1alpha1Workflow:
        """Creates the workflow"""
        if namespace is None:
            namespace = self.namespace
        return self.service.create(self.workflow, namespace)

    def delete(self, namespace: Optional[str] = None) -> Tuple[object, int, dict]:
        """Deletes the workflow"""
        if namespace is None:
            namespace = self.name
        return self.service.delete(self.name)
