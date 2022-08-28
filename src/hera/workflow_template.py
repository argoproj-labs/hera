"""The implementation of a Hera workflowTemplate for Argo-based workflowTemplates"""
from typing import Dict, List, Optional

from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1Arguments,
    IoArgoprojWorkflowV1alpha1DAGTemplate,
    IoArgoprojWorkflowV1alpha1Template,
    IoArgoprojWorkflowV1alpha1WorkflowSpec,
    IoArgoprojWorkflowV1alpha1WorkflowTemplate,
    ObjectMeta,
)

import hera
from hera.affinity import Affinity
from hera.security_context import WorkflowSecurityContext
from hera.task import Task
from hera.ttl_strategy import TTLStrategy
from hera.variable import Variable
from hera.volumes import BaseVolume, Volume
from hera.workflow_editors import add_head, add_tail, add_task, add_tasks, on_exit
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
    service: Optional[WorkflowService] = None
        A workflowTemplate service to use for submissions.
        See `hera.v1.workflow_template_service.WorkflowTemplateService`.
    parallelism: int = 50
        The number of parallel tasks to run in case a task group is executed for multiple tasks.
    service_account_name: Optional[str] = None
        The name of the service account to use in all workflow tasks.
    labels: Optional[Dict[str, str]] = None
        A Dict of labels to attach to the Workflow object metadata
    namespace: Optional[str] = 'default'
        The namespace to use for creating the WorkflowTemplate.  Defaults to "default"
    security_context:  Optional[WorkflowSecurityContext] = None
        Define security settings for all containers in the workflow.
    ttl_strategy: Optional[TTLStrategy] = None
        The time to live strategy of the workflow.
    node_selectors: Optional[Dict[str, str]] = None
        A collection of key value pairs that denote node selectors. This is used for scheduling purposes. If the task
        requires GPU resources, clients are encouraged to add a node selector for a node that can satisfy the
        requested resources. In addition, clients are encouraged to specify a GPU toleration, depending on the platform
        they submit the workflow to.
    affinity: Optional[Affinity] = None
        The task affinity. This dictates the scheduling protocol of the pods running the tasks of the workflow.
    variables: Optional[List[Variable]] = None
        A list of global variables for the workflow. These are accessible by all tasks via `GlobalInputParameter`.
    volumes: Optional[List[BaseVolume]] = None
        List of volumes to mount to all the tasks of the workflow.
    """

    def __init__(
        self,
        name: str,
        service: Optional[WorkflowTemplateService] = None,
        parallelism: int = 50,
        service_account_name: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
        namespace: Optional[str] = None,
        security_context: Optional[WorkflowSecurityContext] = None,
        ttl_strategy: Optional[TTLStrategy] = None,
        node_selectors: Optional[Dict[str, str]] = None,
        affinity: Optional[Affinity] = None,
        variables: Optional[List[Variable]] = None,
        volumes: Optional[List[BaseVolume]] = None,
    ):
        self.name = f'{name.replace("_", "-")}'  # RFC1123
        self.namespace = namespace or "default"
        self.service = service or WorkflowTemplateService()
        self.parallelism = parallelism
        self.security_context = security_context
        self.service_account_name = service_account_name
        self.labels = labels
        self.ttl_strategy = ttl_strategy
        self.node_selector = node_selectors
        self.affinity = affinity
        self.in_context = False
        self.variables = variables
        self.volumes = volumes

        self.dag_template = IoArgoprojWorkflowV1alpha1DAGTemplate(tasks=[])
        self.exit_template = IoArgoprojWorkflowV1alpha1Template(
            name="exit-template",
            steps=[],
            dag=IoArgoprojWorkflowV1alpha1DAGTemplate(tasks=[]),
            parallelism=self.parallelism,
        )

        self.template = IoArgoprojWorkflowV1alpha1Template(
            name=self.name,
            steps=[],
            dag=self.dag_template,
            parallelism=self.parallelism,
        )

        self.spec = IoArgoprojWorkflowV1alpha1WorkflowSpec(
            templates=[self.template],
            entrypoint=self.name,
            volumes=[],
            volume_claim_templates=[],
            parallelism=self.parallelism,
        )
        if self.volumes is not None:
            for volume in self.volumes:
                if isinstance(volume, Volume):
                    self.spec.volume_claim_templates.append(volume.get_claim_spec())
                else:
                    self.spec.volumes.append(volume.get_volume())

        if self.ttl_strategy:
            setattr(self.spec, "ttl_strategy", ttl_strategy.argo_ttl_strategy)

        if self.security_context:
            security_context = self.security_context.get_security_context()
            setattr(self.spec, "security_context", security_context)

        if self.service_account_name:
            setattr(self.template, "service_account_name", self.service_account_name)
            setattr(self.spec, "service_account_name", self.service_account_name)

        if self.affinity:
            setattr(self.exit_template, "affinity", self.affinity.get_spec())
            setattr(self.template, "affinity", self.affinity.get_spec())

        self.metadata = ObjectMeta(name=self.name)
        if self.labels:
            setattr(self.metadata, "labels", self.labels)

        if self.node_selector:
            setattr(self.dag_template, "node_selector", self.node_selector)
            setattr(self.template, "node_selector", self.node_selector)
            setattr(self.exit_template, "node_selector", self.node_selector)

        if self.variables:
            setattr(
                self.spec,
                "arguments",
                IoArgoprojWorkflowV1alpha1Arguments(
                    parameters=[variable.get_argument_parameter() for variable in self.variables],
                ),
            )

        self.workflow_template = IoArgoprojWorkflowV1alpha1WorkflowTemplate(metadata=self.metadata, spec=self.spec)

    def __enter__(self) -> "WorkflowTemplate":
        self.in_context = True
        hera.context.set(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.in_context = False
        hera.context.reset()

    def add_task(self, t: Task) -> None:
        add_task(self, t)

    def add_tasks(self, *ts: Task) -> None:
        add_tasks(self, *ts)

    def add_head(self, t: Task, append: bool = True) -> None:
        add_head(self, t, append=append)

    def add_tail(self, t: Task, append: bool = True) -> None:
        add_tail(self, t, append=append)

    def on_exit(self, *t: Task) -> None:
        on_exit(self, *t)

    def create(self, namespace: Optional[str] = None) -> IoArgoprojWorkflowV1alpha1WorkflowTemplate:
        """Creates the workflow"""
        if self.in_context:
            raise ValueError("Cannot invoke `create` when using a Hera context")
        if namespace is None:
            namespace = self.namespace
        return self.service.create(self.workflow_template, namespace)
