"""The implementation of a Hera cron workflow for Argo-based cron workflows"""
from datetime import datetime
from datetime import timezone as tz
from typing import Dict, List, Optional, Tuple

import pytz
from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1Arguments,
    IoArgoprojWorkflowV1alpha1CronWorkflow,
    IoArgoprojWorkflowV1alpha1CronWorkflowSpec,
    IoArgoprojWorkflowV1alpha1CronWorkflowStatus,
    IoArgoprojWorkflowV1alpha1DAGTemplate,
    IoArgoprojWorkflowV1alpha1Template,
    IoArgoprojWorkflowV1alpha1VolumeClaimGC,
    IoArgoprojWorkflowV1alpha1WorkflowSpec,
    IoArgoprojWorkflowV1alpha1WorkflowTemplateRef,
    LocalObjectReference,
    ObjectMeta,
)

import hera
from hera.affinity import Affinity
from hera.cron_workflow_service import CronWorkflowService
from hera.host_alias import HostAlias
from hera.security_context import WorkflowSecurityContext
from hera.task import Task
from hera.ttl_strategy import TTLStrategy
from hera.variable import Variable
from hera.volume_claim_gc import VolumeClaimGCStrategy
from hera.volumes import BaseVolume, Volume
from hera.workflow_editors import add_head, add_tail, add_task, add_tasks, on_exit


class CronWorkflow:
    """A cron workflow representation.

    CronWorkflow are workflows that run on a preset schedule.
    In essence, CronWorkflow = Workflow + some specific cron options.

    Parameters
    ----------
    name: str
        The cron workflow name. Note that the cron workflow initiation will replace underscores with dashes.
    service: Optional[CronWorkflowService] = None
        A cron workflow service to use for creations. See `hera.v1.cron_workflow_service.CronWorkflowService`.
    timezone: str
        Timezone during which the Workflow will be run from the IANA timezone standard, e.g. America/Los_Angeles.
    schedule: str
        Schedule at which the Workflow will be run in Cron format. E.g. 5 4 * * *.
    parallelism: int = 50
        The number of parallel tasks to run in case a task group is executed for multiple tasks.
    service_account_name: Optional[str] = None
        The name of the service account to use in all workflow tasks.
    labels: Optional[Dict[str, str]] = None
        A Dict of labels to attach to the CronWorkflow object metadata.
    annotations: Optional[Dict[str, str]] = None
        A Dict of annotations to attach to the CronWorkflow object metadata.
    namespace: Optional[str] = 'default'
        The namespace to use by default when calling create/update/suspend/resume.  Defaults to 'default'.
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
    ttl_strategy: Optional[TTLStrategy] = None
        The time to live strategy of the workflow.
    volume_claim_gc_strategy: Optional[VolumeClaimGCStrategy] = None
        Define how to delete volumes from completed Workflows.
    host_aliases: Optional[List[HostAlias]] = None
        Mappings between IP and hostnames.
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
        schedule: str,
        service: Optional[CronWorkflowService] = None,
        timezone: Optional[str] = None,
        parallelism: int = 50,
        service_account_name: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
        annotations: Optional[Dict[str, str]] = None,
        namespace: Optional[str] = "default",
        security_context: Optional[WorkflowSecurityContext] = None,
        image_pull_secrets: Optional[List[str]] = None,
        workflow_template_ref: Optional[str] = None,
        ttl_strategy: Optional[TTLStrategy] = None,
        volume_claim_gc_strategy: Optional[VolumeClaimGCStrategy] = None,
        host_aliases: Optional[List[HostAlias]] = None,
        node_selectors: Optional[Dict[str, str]] = None,
        affinity: Optional[Affinity] = None,
        variables: Optional[List[Variable]] = None,
        volumes: Optional[List[BaseVolume]] = None,
    ):
        if timezone and timezone not in pytz.all_timezones:
            raise ValueError(f"{timezone} is not a valid timezone")

        self.name = name.replace("_", "-")
        self.schedule = schedule
        self.timezone = timezone
        self.service = service or CronWorkflowService()
        self.parallelism = parallelism
        self.service_account_name = service_account_name
        self.labels = labels
        self.annotations = annotations
        self.namespace = namespace
        self.security_context = security_context
        self.image_pull_secrets = image_pull_secrets
        self.workflow_template_ref = workflow_template_ref
        self.node_selector = node_selectors
        self.ttl_strategy = ttl_strategy
        self.affinity = affinity
        self.variables = variables
        self.volumes = volumes
        self.in_context = False

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

        if self.workflow_template_ref:
            self.workflow_template = IoArgoprojWorkflowV1alpha1WorkflowTemplateRef(name=self.workflow_template_ref)
            self.spec = IoArgoprojWorkflowV1alpha1WorkflowSpec(
                workflow_template_ref=self.workflow_template,
                entrypoint=self.workflow_template_ref,
                volumes=[],
                volume_claim_templates=[],
                parallelism=self.parallelism,
            )
        else:
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

        if volume_claim_gc_strategy:
            setattr(
                self.spec,
                "volume_claim_gc",
                IoArgoprojWorkflowV1alpha1VolumeClaimGC(strategy=volume_claim_gc_strategy.value),
            )

        if host_aliases:
            setattr(self.spec, "host_aliases", [h.argo_host_alias for h in host_aliases])

        if self.service_account_name:
            setattr(self.template, "service_account_name", self.service_account_name)
            setattr(self.spec, "service_account_name", self.service_account_name)

        if self.security_context:
            security_context = self.security_context.get_security_context()
            setattr(self.spec, "security_context", security_context)

        if self.image_pull_secrets:
            secret_refs = [LocalObjectReference(name=name) for name in self.image_pull_secrets]
            setattr(self.spec, "image_pull_secrets", secret_refs)

        self.cron_spec = IoArgoprojWorkflowV1alpha1CronWorkflowSpec(schedule=self.schedule, workflow_spec=self.spec)
        if self.timezone:
            setattr(self.cron_spec, "timezone", self.timezone)

        if self.affinity:
            setattr(self.exit_template, "affinity", self.affinity.get_spec())
            setattr(self.template, "affinity", self.affinity.get_spec())

        self.metadata = ObjectMeta(name=self.name)
        if self.labels:
            setattr(self.metadata, "labels", self.labels)
        if self.annotations:
            setattr(self.metadata, "annotations", self.annotations)

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

        self.workflow = IoArgoprojWorkflowV1alpha1CronWorkflow(
            metadata=self.metadata,
            spec=self.cron_spec,
            status=IoArgoprojWorkflowV1alpha1CronWorkflowStatus(
                active=[], conditions=[], last_scheduled_time=datetime.now(tz.utc)
            ),
        )

    def __enter__(self) -> "CronWorkflow":
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

    def create(self, namespace: Optional[str] = None) -> IoArgoprojWorkflowV1alpha1CronWorkflow:
        """Creates the cron workflow in the server"""
        if self.in_context:
            raise ValueError("Cannot invoke `create` when using a Hera context")
        if namespace is None:
            namespace = self.namespace
        return self.service.create(self.workflow, namespace)

    def update(
        self, name: Optional[str] = None, namespace: Optional[str] = None
    ) -> IoArgoprojWorkflowV1alpha1CronWorkflow:
        """Updates the cron workflow in the server"""
        if namespace is None:
            namespace = self.namespace
        if name is None:
            name = self.name

        # When update cron_workflow, metadata.resourceVersion and metadata.uid should be same as the previous value.
        old_workflow = self.service.get_workflow(name, namespace)
        self.workflow.metadata["resourceVersion"] = old_workflow.metadata["resourceVersion"]
        self.workflow.metadata["uid"] = old_workflow.metadata["uid"]

        return self.service.update(self.workflow, name, namespace)

    def suspend(self, name: Optional[str] = None, namespace: Optional[str] = None) -> Tuple[object, int, dict]:
        """Suspends the cron workflow"""
        if name is None:
            name = self.name
        if namespace is None:
            namespace = self.namespace
        return self.service.suspend(name, namespace)

    def resume(self, name: Optional[str] = None, namespace: Optional[str] = None) -> Tuple[object, int, dict]:
        """Resumes execution of the cron workflow"""
        if name is None:
            name = self.name
        if namespace is None:
            namespace = self.namespace
        return self.service.resume(name, namespace)
