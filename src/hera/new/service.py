import os
from typing import Optional

import requests

from hera.models import *
from hera.new.config import GlobalConfig


class Service:
    def __init__(
        self,
        host: Optional[str] = None,
        verify_ssl: bool = True,
        token: Optional[str] = None,
        namespace: Optional[str] = None,
    ):
        self.host = host or GlobalConfig.host
        self.verify_ssl = verify_ssl or GlobalConfig.verify_ssl
        self.token = token or GlobalConfig.token
        self.namespace = namespace or GlobalConfig.namespace

    def list_archived_workflows(
        self,
        label_selector: Optional[str] = None,
        field_selector: Optional[str] = None,
        watch: Optional[bool] = None,
        allow_watch_bookmarks: Optional[bool] = None,
        resource_version: Optional[str] = None,
        resource_version_match: Optional[str] = None,
        timeout_seconds: Optional[str] = None,
        limit: Optional[str] = None,
        continue_: Optional[str] = None,
        name_prefix: Optional[str] = None,
    ) -> WorkflowList:
        resp = requests.get(
            url=os.path.join(self.host, "/api/v1/archived-workflows"),
            params={
                "listOptions.labelSelector": label_selector,
                "listOptions.fieldSelector": field_selector,
                "listOptions.watch": watch,
                "listOptions.allowWatchBookmarks": allow_watch_bookmarks,
                "listOptions.resourceVersion": resource_version,
                "listOptions.resourceVersionMatch": resource_version_match,
                "listOptions.timeoutSeconds": timeout_seconds,
                "listOptions.limit": limit,
                "listOptions.continue": continue_,
                "namePrefix": name_prefix,
            },
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        ).json()
        return WorkflowList(**resp)

    def list_archived_workflow_label_keys(self) -> LabelKeys:
        resp = requests.get(
            url=os.path.join(self.host, "/api/v1/archived-workflows-label-keys"),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        ).json()
        return LabelKeys(**resp)

    def list_archived_workflow_label_values(
        self,
        label_selector: Optional[str] = None,
        field_selector: Optional[str] = None,
        watch: Optional[bool] = None,
        allow_watch_bookmarks: Optional[bool] = None,
        resource_version: Optional[str] = None,
        resource_version_match: Optional[str] = None,
        timeout_seconds: Optional[str] = None,
        limit: Optional[str] = None,
        continue_: Optional[str] = None,
    ) -> LabelValues:
        resp = requests.get(
            url=os.path.join(self.host, "/api/v1/archived-workflows-label-values"),
            params={
                "listOptions.labelSelector": label_selector,
                "listOptions.fieldSelector": field_selector,
                "listOptions.watch": watch,
                "listOptions.allowWatchBookmarks": allow_watch_bookmarks,
                "listOptions.resourceVersion": resource_version,
                "listOptions.resourceVersionMatch": resource_version_match,
                "listOptions.timeoutSeconds": timeout_seconds,
                "listOptions.limit": limit,
                "listOptions.continue": continue_,
            },
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        ).json()
        return LabelValues(**resp)

    def get_archived_workflow(self, uid: str) -> Workflow:
        resp = requests.get(
            url=os.path.join(self.host, "/api/v1/archived-workflows/{uid}").format(uid=uid),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        ).json()
        return Workflow(**resp)

    def delete_archived_workflow(self, uid: str) -> ArchivedWorkflowDeletedResponse:
        _ = requests.delete(
            url=os.path.join(self.host, "/api/v1/archived-workflows/{uid}").format(uid=uid),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        ).json()
        return ArchivedWorkflowDeletedResponse()

    def resubmit_archived_workflow(self, uid: str, req: ResubmitArchivedWorkflowRequest) -> Workflow:
        resp = requests.put(
            url=os.path.join(self.host, "/api/v1/archived-workflows/{uid}/resubmit").format(uid=uid),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(),
            verify=self.verify_ssl,
        ).json()
        return Workflow(**resp)

    def retry_archived_workflow(self, uid: str, req: RetryArchivedWorkflowRequest) -> Workflow:
        resp = requests.put(
            url=os.path.join(self.host, "/api/v1/archived-workflows/{uid}/retry").format(uid=uid),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(),
            verify=self.verify_ssl,
        ).json()
        return Workflow(**resp)

    def list_cluster_workflow_templates(
        self,
        label_selector: Optional[str] = None,
        field_selector: Optional[str] = None,
        watch: Optional[bool] = None,
        allow_watch_bookmarks: Optional[bool] = None,
        resource_version: Optional[str] = None,
        resource_version_match: Optional[str] = None,
        timeout_seconds: Optional[str] = None,
        limit: Optional[str] = None,
        continue_: Optional[str] = None,
    ) -> ClusterWorkflowTemplateList:
        resp = requests.get(
            url=os.path.join(self.host, "/api/v1/cluster-workflow-templates"),
            params={
                "listOptions.labelSelector": label_selector,
                "listOptions.fieldSelector": field_selector,
                "listOptions.watch": watch,
                "listOptions.allowWatchBookmarks": allow_watch_bookmarks,
                "listOptions.resourceVersion": resource_version,
                "listOptions.resourceVersionMatch": resource_version_match,
                "listOptions.timeoutSeconds": timeout_seconds,
                "listOptions.limit": limit,
                "listOptions.continue": continue_,
            },
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        ).json()
        return ClusterWorkflowTemplateList(**resp)

    def create_cluster_workflow_template(self, req: ClusterWorkflowTemplateCreateRequest) -> ClusterWorkflowTemplate:
        resp = requests.post(
            url=os.path.join(self.host, "/api/v1/cluster-workflow-templates"),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(),
            verify=self.verify_ssl,
        ).json()
        return ClusterWorkflowTemplate(**resp)

    def lint_cluster_workflow_template(self, req: ClusterWorkflowTemplateLintRequest) -> ClusterWorkflowTemplate:
        resp = requests.post(
            url=os.path.join(self.host, "/api/v1/cluster-workflow-templates/lint"),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(),
            verify=self.verify_ssl,
        ).json()
        return ClusterWorkflowTemplate(**resp)

    def get_cluster_workflow_template(
        self, name: str, resource_version: Optional[str] = None
    ) -> ClusterWorkflowTemplate:
        resp = requests.get(
            url=os.path.join(self.host, "/api/v1/cluster-workflow-templates/{name}").format(name=name),
            params={"getOptions.resourceVersion": resource_version},
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        ).json()
        return ClusterWorkflowTemplate(**resp)

    def update_cluster_workflow_template(
        self, name: str, req: ClusterWorkflowTemplateUpdateRequest
    ) -> ClusterWorkflowTemplate:
        resp = requests.put(
            url=os.path.join(self.host, "/api/v1/cluster-workflow-templates/{name}").format(name=name),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(),
            verify=self.verify_ssl,
        ).json()
        return ClusterWorkflowTemplate(**resp)

    def delete_cluster_workflow_template(
        self,
        name: str,
        grace_period_seconds: Optional[str] = None,
        uid: Optional[str] = None,
        resource_version: Optional[str] = None,
        orphan_dependents: Optional[bool] = None,
        propagation_policy: Optional[str] = None,
        dry_run: Optional[list] = None,
    ) -> ClusterWorkflowTemplateDeleteResponse:
        _ = requests.delete(
            url=os.path.join(self.host, "/api/v1/cluster-workflow-templates/{name}").format(name=name),
            params={
                "deleteOptions.gracePeriodSeconds": grace_period_seconds,
                "deleteOptions.preconditions.uid": uid,
                "deleteOptions.preconditions.resourceVersion": resource_version,
                "deleteOptions.orphanDependents": orphan_dependents,
                "deleteOptions.propagationPolicy": propagation_policy,
                "deleteOptions.dryRun": dry_run,
            },
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        ).json()
        return ClusterWorkflowTemplateDeleteResponse()

    def list_cron_workflows(
        self,
        namespace: str,
        label_selector: Optional[str] = None,
        field_selector: Optional[str] = None,
        watch: Optional[bool] = None,
        allow_watch_bookmarks: Optional[bool] = None,
        resource_version: Optional[str] = None,
        resource_version_match: Optional[str] = None,
        timeout_seconds: Optional[str] = None,
        limit: Optional[str] = None,
        continue_: Optional[str] = None,
    ) -> CronWorkflowList:
        resp = requests.get(
            url=os.path.join(self.host, "/api/v1/cron-workflows/{namespace}").format(namespace=namespace),
            params={
                "listOptions.labelSelector": label_selector,
                "listOptions.fieldSelector": field_selector,
                "listOptions.watch": watch,
                "listOptions.allowWatchBookmarks": allow_watch_bookmarks,
                "listOptions.resourceVersion": resource_version,
                "listOptions.resourceVersionMatch": resource_version_match,
                "listOptions.timeoutSeconds": timeout_seconds,
                "listOptions.limit": limit,
                "listOptions.continue": continue_,
            },
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        ).json()
        return CronWorkflowList(**resp)

    def create_cron_workflow(self, namespace: str, req: CreateCronWorkflowRequest) -> CronWorkflow:
        resp = requests.post(
            url=os.path.join(self.host, "/api/v1/cron-workflows/{namespace}").format(namespace=namespace),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(),
            verify=self.verify_ssl,
        ).json()
        return CronWorkflow(**resp)

    def lint_cron_workflow(self, namespace: str, req: LintCronWorkflowRequest) -> CronWorkflow:
        resp = requests.post(
            url=os.path.join(self.host, "/api/v1/cron-workflows/{namespace}/lint").format(namespace=namespace),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(),
            verify=self.verify_ssl,
        ).json()
        return CronWorkflow(**resp)

    def get_cron_workflow(self, namespace: str, name: str, resource_version: Optional[str] = None) -> CronWorkflow:
        resp = requests.get(
            url=os.path.join(self.host, "/api/v1/cron-workflows/{namespace}/{name}").format(
                namespace=namespace, name=name
            ),
            params={"getOptions.resourceVersion": resource_version},
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        ).json()
        return CronWorkflow(**resp)

    def update_cron_workflow(self, namespace: str, name: str, req: UpdateCronWorkflowRequest) -> CronWorkflow:
        resp = requests.put(
            url=os.path.join(self.host, "/api/v1/cron-workflows/{namespace}/{name}").format(
                namespace=namespace, name=name
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(),
            verify=self.verify_ssl,
        ).json()
        return CronWorkflow(**resp)

    def delete_cron_workflow(
        self,
        namespace: str,
        name: str,
        grace_period_seconds: Optional[str] = None,
        uid: Optional[str] = None,
        resource_version: Optional[str] = None,
        orphan_dependents: Optional[bool] = None,
        propagation_policy: Optional[str] = None,
        dry_run: Optional[list] = None,
    ) -> CronWorkflowDeletedResponse:
        _ = requests.delete(
            url=os.path.join(self.host, "/api/v1/cron-workflows/{namespace}/{name}").format(
                namespace=namespace, name=name
            ),
            params={
                "deleteOptions.gracePeriodSeconds": grace_period_seconds,
                "deleteOptions.preconditions.uid": uid,
                "deleteOptions.preconditions.resourceVersion": resource_version,
                "deleteOptions.orphanDependents": orphan_dependents,
                "deleteOptions.propagationPolicy": propagation_policy,
                "deleteOptions.dryRun": dry_run,
            },
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        ).json()
        return CronWorkflowDeletedResponse()

    def resume_cron_workflow(self, namespace: str, name: str, req: CronWorkflowResumeRequest) -> CronWorkflow:
        resp = requests.put(
            url=os.path.join(self.host, "/api/v1/cron-workflows/{namespace}/{name}/resume").format(
                namespace=namespace, name=name
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(),
            verify=self.verify_ssl,
        ).json()
        return CronWorkflow(**resp)

    def suspend_cron_workflow(self, namespace: str, name: str, req: CronWorkflowSuspendRequest) -> CronWorkflow:
        resp = requests.put(
            url=os.path.join(self.host, "/api/v1/cron-workflows/{namespace}/{name}/suspend").format(
                namespace=namespace, name=name
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(),
            verify=self.verify_ssl,
        ).json()
        return CronWorkflow(**resp)

    def list_event_sources(
        self,
        namespace: str,
        label_selector: Optional[str] = None,
        field_selector: Optional[str] = None,
        watch: Optional[bool] = None,
        allow_watch_bookmarks: Optional[bool] = None,
        resource_version: Optional[str] = None,
        resource_version_match: Optional[str] = None,
        timeout_seconds: Optional[str] = None,
        limit: Optional[str] = None,
        continue_: Optional[str] = None,
    ) -> EventSourceList:
        resp = requests.get(
            url=os.path.join(self.host, "/api/v1/event-sources/{namespace}").format(namespace=namespace),
            params={
                "listOptions.labelSelector": label_selector,
                "listOptions.fieldSelector": field_selector,
                "listOptions.watch": watch,
                "listOptions.allowWatchBookmarks": allow_watch_bookmarks,
                "listOptions.resourceVersion": resource_version,
                "listOptions.resourceVersionMatch": resource_version_match,
                "listOptions.timeoutSeconds": timeout_seconds,
                "listOptions.limit": limit,
                "listOptions.continue": continue_,
            },
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        ).json()
        return EventSourceList(**resp)

    def create_event_source(self, namespace: str, req: CreateEventSourceRequest) -> EventSource:
        resp = requests.post(
            url=os.path.join(self.host, "/api/v1/event-sources/{namespace}").format(namespace=namespace),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(),
            verify=self.verify_ssl,
        ).json()
        return EventSource(**resp)

    def get_event_source(self, namespace: str, name: str) -> EventSource:
        resp = requests.get(
            url=os.path.join(self.host, "/api/v1/event-sources/{namespace}/{name}").format(
                namespace=namespace, name=name
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        ).json()
        return EventSource(**resp)

    def update_event_source(self, namespace: str, name: str, req: UpdateEventSourceRequest) -> EventSource:
        resp = requests.put(
            url=os.path.join(self.host, "/api/v1/event-sources/{namespace}/{name}").format(
                namespace=namespace, name=name
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(),
            verify=self.verify_ssl,
        ).json()
        return EventSource(**resp)

    def delete_event_source(
        self,
        namespace: str,
        name: str,
        grace_period_seconds: Optional[str] = None,
        uid: Optional[str] = None,
        resource_version: Optional[str] = None,
        orphan_dependents: Optional[bool] = None,
        propagation_policy: Optional[str] = None,
        dry_run: Optional[list] = None,
    ) -> EventSourceDeletedResponse:
        _ = requests.delete(
            url=os.path.join(self.host, "/api/v1/event-sources/{namespace}/{name}").format(
                namespace=namespace, name=name
            ),
            params={
                "deleteOptions.gracePeriodSeconds": grace_period_seconds,
                "deleteOptions.preconditions.uid": uid,
                "deleteOptions.preconditions.resourceVersion": resource_version,
                "deleteOptions.orphanDependents": orphan_dependents,
                "deleteOptions.propagationPolicy": propagation_policy,
                "deleteOptions.dryRun": dry_run,
            },
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        ).json()
        return EventSourceDeletedResponse()

    def receive_event(self, namespace: str, discriminator: str, req: Item) -> EventResponse:
        _ = requests.post(
            url=os.path.join(self.host, "/api/v1/events/{namespace}/{discriminator}").format(
                namespace=namespace, discriminator=discriminator
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(),
            verify=self.verify_ssl,
        ).json()
        return EventResponse()

    def get_info(self) -> InfoResponse:
        _ = requests.get(
            url=os.path.join(self.host, "/api/v1/info"),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        ).json()
        return InfoResponse()

    def list_sensors(
        self,
        namespace: str,
        label_selector: Optional[str] = None,
        field_selector: Optional[str] = None,
        watch: Optional[bool] = None,
        allow_watch_bookmarks: Optional[bool] = None,
        resource_version: Optional[str] = None,
        resource_version_match: Optional[str] = None,
        timeout_seconds: Optional[str] = None,
        limit: Optional[str] = None,
        continue_: Optional[str] = None,
    ) -> SensorList:
        resp = requests.get(
            url=os.path.join(self.host, "/api/v1/sensors/{namespace}").format(namespace=namespace),
            params={
                "listOptions.labelSelector": label_selector,
                "listOptions.fieldSelector": field_selector,
                "listOptions.watch": watch,
                "listOptions.allowWatchBookmarks": allow_watch_bookmarks,
                "listOptions.resourceVersion": resource_version,
                "listOptions.resourceVersionMatch": resource_version_match,
                "listOptions.timeoutSeconds": timeout_seconds,
                "listOptions.limit": limit,
                "listOptions.continue": continue_,
            },
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        ).json()
        return SensorList(**resp)

    def create_sensor(self, namespace: str, req: CreateSensorRequest) -> Sensor:
        resp = requests.post(
            url=os.path.join(self.host, "/api/v1/sensors/{namespace}").format(namespace=namespace),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(),
            verify=self.verify_ssl,
        ).json()
        return Sensor(**resp)

    def get_sensor(self, namespace: str, name: str, resource_version: Optional[str] = None) -> Sensor:
        resp = requests.get(
            url=os.path.join(self.host, "/api/v1/sensors/{namespace}/{name}").format(namespace=namespace, name=name),
            params={"getOptions.resourceVersion": resource_version},
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        ).json()
        return Sensor(**resp)

    def update_sensor(self, namespace: str, name: str, req: UpdateSensorRequest) -> Sensor:
        resp = requests.put(
            url=os.path.join(self.host, "/api/v1/sensors/{namespace}/{name}").format(namespace=namespace, name=name),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(),
            verify=self.verify_ssl,
        ).json()
        return Sensor(**resp)

    def delete_sensor(
        self,
        namespace: str,
        name: str,
        grace_period_seconds: Optional[str] = None,
        uid: Optional[str] = None,
        resource_version: Optional[str] = None,
        orphan_dependents: Optional[bool] = None,
        propagation_policy: Optional[str] = None,
        dry_run: Optional[list] = None,
    ) -> DeleteSensorResponse:
        _ = requests.delete(
            url=os.path.join(self.host, "/api/v1/sensors/{namespace}/{name}").format(namespace=namespace, name=name),
            params={
                "deleteOptions.gracePeriodSeconds": grace_period_seconds,
                "deleteOptions.preconditions.uid": uid,
                "deleteOptions.preconditions.resourceVersion": resource_version,
                "deleteOptions.orphanDependents": orphan_dependents,
                "deleteOptions.propagationPolicy": propagation_policy,
                "deleteOptions.dryRun": dry_run,
            },
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        ).json()
        return DeleteSensorResponse()

    def watch_event_sources(
        self,
        namespace: str,
        label_selector: Optional[str] = None,
        field_selector: Optional[str] = None,
        watch: Optional[bool] = None,
        allow_watch_bookmarks: Optional[bool] = None,
        resource_version: Optional[str] = None,
        resource_version_match: Optional[str] = None,
        timeout_seconds: Optional[str] = None,
        limit: Optional[str] = None,
        continue_: Optional[str] = None,
    ) -> EventSourceWatchEvent:
        resp = requests.get(
            url=os.path.join(self.host, "/api/v1/stream/event-sources/{namespace}").format(namespace=namespace),
            params={
                "listOptions.labelSelector": label_selector,
                "listOptions.fieldSelector": field_selector,
                "listOptions.watch": watch,
                "listOptions.allowWatchBookmarks": allow_watch_bookmarks,
                "listOptions.resourceVersion": resource_version,
                "listOptions.resourceVersionMatch": resource_version_match,
                "listOptions.timeoutSeconds": timeout_seconds,
                "listOptions.limit": limit,
                "listOptions.continue": continue_,
            },
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        ).json()
        return EventSourceWatchEvent(**resp)

    def event_sources_logs(
        self,
        namespace: str,
        name: Optional[str] = None,
        event_source_type: Optional[str] = None,
        event_name: Optional[str] = None,
        grep: Optional[str] = None,
        container: Optional[str] = None,
        follow: Optional[bool] = None,
        previous: Optional[bool] = None,
        since_seconds: Optional[str] = None,
        seconds: Optional[str] = None,
        nanos: Optional[int] = None,
        timestamps: Optional[bool] = None,
        tail_lines: Optional[str] = None,
        limit_bytes: Optional[str] = None,
        insecure_skip_tls_verify_backend: Optional[bool] = None,
    ) -> LogEntry:
        resp = requests.get(
            url=os.path.join(self.host, "/api/v1/stream/event-sources/{namespace}/logs").format(namespace=namespace),
            params={
                "name": name,
                "eventSourceType": event_source_type,
                "eventName": event_name,
                "grep": grep,
                "podLogOptions.container": container,
                "podLogOptions.follow": follow,
                "podLogOptions.previous": previous,
                "podLogOptions.sinceSeconds": since_seconds,
                "podLogOptions.sinceTime.seconds": seconds,
                "podLogOptions.sinceTime.nanos": nanos,
                "podLogOptions.timestamps": timestamps,
                "podLogOptions.tailLines": tail_lines,
                "podLogOptions.limitBytes": limit_bytes,
                "podLogOptions.insecureSkipTLSVerifyBackend": insecure_skip_tls_verify_backend,
            },
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        ).json()
        return LogEntry(**resp)

    def watch_events(
        self,
        namespace: str,
        label_selector: Optional[str] = None,
        field_selector: Optional[str] = None,
        watch: Optional[bool] = None,
        allow_watch_bookmarks: Optional[bool] = None,
        resource_version: Optional[str] = None,
        resource_version_match: Optional[str] = None,
        timeout_seconds: Optional[str] = None,
        limit: Optional[str] = None,
        continue_: Optional[str] = None,
    ) -> Event:
        resp = requests.get(
            url=os.path.join(self.host, "/api/v1/stream/events/{namespace}").format(namespace=namespace),
            params={
                "listOptions.labelSelector": label_selector,
                "listOptions.fieldSelector": field_selector,
                "listOptions.watch": watch,
                "listOptions.allowWatchBookmarks": allow_watch_bookmarks,
                "listOptions.resourceVersion": resource_version,
                "listOptions.resourceVersionMatch": resource_version_match,
                "listOptions.timeoutSeconds": timeout_seconds,
                "listOptions.limit": limit,
                "listOptions.continue": continue_,
            },
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        ).json()
        return Event(**resp)

    def watch_sensors(
        self,
        namespace: str,
        label_selector: Optional[str] = None,
        field_selector: Optional[str] = None,
        watch: Optional[bool] = None,
        allow_watch_bookmarks: Optional[bool] = None,
        resource_version: Optional[str] = None,
        resource_version_match: Optional[str] = None,
        timeout_seconds: Optional[str] = None,
        limit: Optional[str] = None,
        continue_: Optional[str] = None,
    ) -> SensorWatchEvent:
        resp = requests.get(
            url=os.path.join(self.host, "/api/v1/stream/sensors/{namespace}").format(namespace=namespace),
            params={
                "listOptions.labelSelector": label_selector,
                "listOptions.fieldSelector": field_selector,
                "listOptions.watch": watch,
                "listOptions.allowWatchBookmarks": allow_watch_bookmarks,
                "listOptions.resourceVersion": resource_version,
                "listOptions.resourceVersionMatch": resource_version_match,
                "listOptions.timeoutSeconds": timeout_seconds,
                "listOptions.limit": limit,
                "listOptions.continue": continue_,
            },
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        ).json()
        return SensorWatchEvent(**resp)

    def sensors_logs(
        self,
        namespace: str,
        name: Optional[str] = None,
        trigger_name: Optional[str] = None,
        grep: Optional[str] = None,
        container: Optional[str] = None,
        follow: Optional[bool] = None,
        previous: Optional[bool] = None,
        since_seconds: Optional[str] = None,
        seconds: Optional[str] = None,
        nanos: Optional[int] = None,
        timestamps: Optional[bool] = None,
        tail_lines: Optional[str] = None,
        limit_bytes: Optional[str] = None,
        insecure_skip_tls_verify_backend: Optional[bool] = None,
    ) -> LogEntry:
        resp = requests.get(
            url=os.path.join(self.host, "/api/v1/stream/sensors/{namespace}/logs").format(namespace=namespace),
            params={
                "name": name,
                "triggerName": trigger_name,
                "grep": grep,
                "podLogOptions.container": container,
                "podLogOptions.follow": follow,
                "podLogOptions.previous": previous,
                "podLogOptions.sinceSeconds": since_seconds,
                "podLogOptions.sinceTime.seconds": seconds,
                "podLogOptions.sinceTime.nanos": nanos,
                "podLogOptions.timestamps": timestamps,
                "podLogOptions.tailLines": tail_lines,
                "podLogOptions.limitBytes": limit_bytes,
                "podLogOptions.insecureSkipTLSVerifyBackend": insecure_skip_tls_verify_backend,
            },
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        ).json()
        return LogEntry(**resp)

    def collect_event(self, req: CollectEventRequest) -> CollectEventResponse:
        _ = requests.post(
            url=os.path.join(self.host, "/api/v1/tracking/event"),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(),
            verify=self.verify_ssl,
        ).json()
        return CollectEventResponse()

    def get_user_info(self) -> GetUserInfoResponse:
        _ = requests.get(
            url=os.path.join(self.host, "/api/v1/userinfo"),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        ).json()
        return GetUserInfoResponse()

    def get_version(self) -> Version:
        resp = requests.get(
            url=os.path.join(self.host, "/api/v1/version"),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        ).json()
        return Version(**resp)

    def list_workflow_event_bindings(
        self,
        namespace: str,
        label_selector: Optional[str] = None,
        field_selector: Optional[str] = None,
        watch: Optional[bool] = None,
        allow_watch_bookmarks: Optional[bool] = None,
        resource_version: Optional[str] = None,
        resource_version_match: Optional[str] = None,
        timeout_seconds: Optional[str] = None,
        limit: Optional[str] = None,
        continue_: Optional[str] = None,
    ) -> WorkflowEventBindingList:
        resp = requests.get(
            url=os.path.join(self.host, "/api/v1/workflow-event-bindings/{namespace}").format(namespace=namespace),
            params={
                "listOptions.labelSelector": label_selector,
                "listOptions.fieldSelector": field_selector,
                "listOptions.watch": watch,
                "listOptions.allowWatchBookmarks": allow_watch_bookmarks,
                "listOptions.resourceVersion": resource_version,
                "listOptions.resourceVersionMatch": resource_version_match,
                "listOptions.timeoutSeconds": timeout_seconds,
                "listOptions.limit": limit,
                "listOptions.continue": continue_,
            },
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        ).json()
        return WorkflowEventBindingList(**resp)

    def watch_workflows(
        self,
        namespace: str,
        label_selector: Optional[str] = None,
        field_selector: Optional[str] = None,
        watch: Optional[bool] = None,
        allow_watch_bookmarks: Optional[bool] = None,
        resource_version: Optional[str] = None,
        resource_version_match: Optional[str] = None,
        timeout_seconds: Optional[str] = None,
        limit: Optional[str] = None,
        continue_: Optional[str] = None,
        fields: Optional[str] = None,
    ) -> WorkflowWatchEvent:
        resp = requests.get(
            url=os.path.join(self.host, "/api/v1/workflow-events/{namespace}").format(namespace=namespace),
            params={
                "listOptions.labelSelector": label_selector,
                "listOptions.fieldSelector": field_selector,
                "listOptions.watch": watch,
                "listOptions.allowWatchBookmarks": allow_watch_bookmarks,
                "listOptions.resourceVersion": resource_version,
                "listOptions.resourceVersionMatch": resource_version_match,
                "listOptions.timeoutSeconds": timeout_seconds,
                "listOptions.limit": limit,
                "listOptions.continue": continue_,
                "fields": fields,
            },
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        ).json()
        return WorkflowWatchEvent(**resp)

    def list_workflow_templates(
        self,
        namespace: str,
        label_selector: Optional[str] = None,
        field_selector: Optional[str] = None,
        watch: Optional[bool] = None,
        allow_watch_bookmarks: Optional[bool] = None,
        resource_version: Optional[str] = None,
        resource_version_match: Optional[str] = None,
        timeout_seconds: Optional[str] = None,
        limit: Optional[str] = None,
        continue_: Optional[str] = None,
    ) -> WorkflowTemplateList:
        resp = requests.get(
            url=os.path.join(self.host, "/api/v1/workflow-templates/{namespace}").format(namespace=namespace),
            params={
                "listOptions.labelSelector": label_selector,
                "listOptions.fieldSelector": field_selector,
                "listOptions.watch": watch,
                "listOptions.allowWatchBookmarks": allow_watch_bookmarks,
                "listOptions.resourceVersion": resource_version,
                "listOptions.resourceVersionMatch": resource_version_match,
                "listOptions.timeoutSeconds": timeout_seconds,
                "listOptions.limit": limit,
                "listOptions.continue": continue_,
            },
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        ).json()
        return WorkflowTemplateList(**resp)

    def create_workflow_template(self, namespace: str, req: WorkflowTemplateCreateRequest) -> WorkflowTemplate:
        resp = requests.post(
            url=os.path.join(self.host, "/api/v1/workflow-templates/{namespace}").format(namespace=namespace),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(),
            verify=self.verify_ssl,
        ).json()
        return WorkflowTemplate(**resp)

    def lint_workflow_template(self, namespace: str, req: WorkflowTemplateLintRequest) -> WorkflowTemplate:
        resp = requests.post(
            url=os.path.join(self.host, "/api/v1/workflow-templates/{namespace}/lint").format(namespace=namespace),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(),
            verify=self.verify_ssl,
        ).json()
        return WorkflowTemplate(**resp)

    def get_workflow_template(
        self, namespace: str, name: str, resource_version: Optional[str] = None
    ) -> WorkflowTemplate:
        resp = requests.get(
            url=os.path.join(self.host, "/api/v1/workflow-templates/{namespace}/{name}").format(
                namespace=namespace, name=name
            ),
            params={"getOptions.resourceVersion": resource_version},
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        ).json()
        return WorkflowTemplate(**resp)

    def update_workflow_template(
        self, namespace: str, name: str, req: WorkflowTemplateUpdateRequest
    ) -> WorkflowTemplate:
        resp = requests.put(
            url=os.path.join(self.host, "/api/v1/workflow-templates/{namespace}/{name}").format(
                namespace=namespace, name=name
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(),
            verify=self.verify_ssl,
        ).json()
        return WorkflowTemplate(**resp)

    def delete_workflow_template(
        self,
        namespace: str,
        name: str,
        grace_period_seconds: Optional[str] = None,
        uid: Optional[str] = None,
        resource_version: Optional[str] = None,
        orphan_dependents: Optional[bool] = None,
        propagation_policy: Optional[str] = None,
        dry_run: Optional[list] = None,
    ) -> WorkflowTemplateDeleteResponse:
        _ = requests.delete(
            url=os.path.join(self.host, "/api/v1/workflow-templates/{namespace}/{name}").format(
                namespace=namespace, name=name
            ),
            params={
                "deleteOptions.gracePeriodSeconds": grace_period_seconds,
                "deleteOptions.preconditions.uid": uid,
                "deleteOptions.preconditions.resourceVersion": resource_version,
                "deleteOptions.orphanDependents": orphan_dependents,
                "deleteOptions.propagationPolicy": propagation_policy,
                "deleteOptions.dryRun": dry_run,
            },
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        ).json()
        return WorkflowTemplateDeleteResponse()

    def list_workflows(
        self,
        namespace: str,
        label_selector: Optional[str] = None,
        field_selector: Optional[str] = None,
        watch: Optional[bool] = None,
        allow_watch_bookmarks: Optional[bool] = None,
        resource_version: Optional[str] = None,
        resource_version_match: Optional[str] = None,
        timeout_seconds: Optional[str] = None,
        limit: Optional[str] = None,
        continue_: Optional[str] = None,
        fields: Optional[str] = None,
    ) -> WorkflowList:
        resp = requests.get(
            url=os.path.join(self.host, "/api/v1/workflows/{namespace}").format(namespace=namespace),
            params={
                "listOptions.labelSelector": label_selector,
                "listOptions.fieldSelector": field_selector,
                "listOptions.watch": watch,
                "listOptions.allowWatchBookmarks": allow_watch_bookmarks,
                "listOptions.resourceVersion": resource_version,
                "listOptions.resourceVersionMatch": resource_version_match,
                "listOptions.timeoutSeconds": timeout_seconds,
                "listOptions.limit": limit,
                "listOptions.continue": continue_,
                "fields": fields,
            },
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        ).json()
        return WorkflowList(**resp)

    def create_workflow(self, namespace: str, req: WorkflowCreateRequest) -> Workflow:
        resp = requests.post(
            url=os.path.join(self.host, "/api/v1/workflows/{namespace}").format(namespace=namespace),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(),
            verify=self.verify_ssl,
        ).json()
        return Workflow(**resp)

    def lint_workflow(self, namespace: str, req: WorkflowLintRequest) -> Workflow:
        resp = requests.post(
            url=os.path.join(self.host, "/api/v1/workflows/{namespace}/lint").format(namespace=namespace),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(),
            verify=self.verify_ssl,
        ).json()
        return Workflow(**resp)

    def submit_workflow(self, namespace: str, req: WorkflowSubmitRequest) -> Workflow:
        resp = requests.post(
            url=os.path.join(self.host, "/api/v1/workflows/{namespace}/submit").format(namespace=namespace),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(),
            verify=self.verify_ssl,
        ).json()
        return Workflow(**resp)

    def get_workflow(
        self, namespace: str, name: str, resource_version: Optional[str] = None, fields: Optional[str] = None
    ) -> Workflow:
        resp = requests.get(
            url=os.path.join(self.host, "/api/v1/workflows/{namespace}/{name}").format(namespace=namespace, name=name),
            params={"getOptions.resourceVersion": resource_version, "fields": fields},
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        ).json()
        return Workflow(**resp)

    def delete_workflow(
        self,
        namespace: str,
        name: str,
        grace_period_seconds: Optional[str] = None,
        uid: Optional[str] = None,
        resource_version: Optional[str] = None,
        orphan_dependents: Optional[bool] = None,
        propagation_policy: Optional[str] = None,
        dry_run: Optional[list] = None,
        force: Optional[bool] = None,
    ) -> WorkflowDeleteResponse:
        _ = requests.delete(
            url=os.path.join(self.host, "/api/v1/workflows/{namespace}/{name}").format(namespace=namespace, name=name),
            params={
                "deleteOptions.gracePeriodSeconds": grace_period_seconds,
                "deleteOptions.preconditions.uid": uid,
                "deleteOptions.preconditions.resourceVersion": resource_version,
                "deleteOptions.orphanDependents": orphan_dependents,
                "deleteOptions.propagationPolicy": propagation_policy,
                "deleteOptions.dryRun": dry_run,
                "force": force,
            },
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        ).json()
        return WorkflowDeleteResponse()

    def workflow_logs(
        self,
        namespace: str,
        name: str,
        pod_name: Optional[str] = None,
        container: Optional[str] = None,
        follow: Optional[bool] = None,
        previous: Optional[bool] = None,
        since_seconds: Optional[str] = None,
        seconds: Optional[str] = None,
        nanos: Optional[int] = None,
        timestamps: Optional[bool] = None,
        tail_lines: Optional[str] = None,
        limit_bytes: Optional[str] = None,
        insecure_skip_tls_verify_backend: Optional[bool] = None,
        grep: Optional[str] = None,
        selector: Optional[str] = None,
    ) -> LogEntry:
        resp = requests.get(
            url=os.path.join(self.host, "/api/v1/workflows/{namespace}/{name}/log").format(
                namespace=namespace, name=name
            ),
            params={
                "podName": pod_name,
                "logOptions.container": container,
                "logOptions.follow": follow,
                "logOptions.previous": previous,
                "logOptions.sinceSeconds": since_seconds,
                "logOptions.sinceTime.seconds": seconds,
                "logOptions.sinceTime.nanos": nanos,
                "logOptions.timestamps": timestamps,
                "logOptions.tailLines": tail_lines,
                "logOptions.limitBytes": limit_bytes,
                "logOptions.insecureSkipTLSVerifyBackend": insecure_skip_tls_verify_backend,
                "grep": grep,
                "selector": selector,
            },
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        ).json()
        return LogEntry(**resp)

    def resubmit_workflow(self, namespace: str, name: str, req: WorkflowResubmitRequest) -> Workflow:
        resp = requests.put(
            url=os.path.join(self.host, "/api/v1/workflows/{namespace}/{name}/resubmit").format(
                namespace=namespace, name=name
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(),
            verify=self.verify_ssl,
        ).json()
        return Workflow(**resp)

    def resume_workflow(self, namespace: str, name: str, req: WorkflowResumeRequest) -> Workflow:
        resp = requests.put(
            url=os.path.join(self.host, "/api/v1/workflows/{namespace}/{name}/resume").format(
                namespace=namespace, name=name
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(),
            verify=self.verify_ssl,
        ).json()
        return Workflow(**resp)

    def retry_workflow(self, namespace: str, name: str, req: WorkflowRetryRequest) -> Workflow:
        resp = requests.put(
            url=os.path.join(self.host, "/api/v1/workflows/{namespace}/{name}/retry").format(
                namespace=namespace, name=name
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(),
            verify=self.verify_ssl,
        ).json()
        return Workflow(**resp)

    def set_workflow(self, namespace: str, name: str, req: WorkflowSetRequest) -> Workflow:
        resp = requests.put(
            url=os.path.join(self.host, "/api/v1/workflows/{namespace}/{name}/set").format(
                namespace=namespace, name=name
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(),
            verify=self.verify_ssl,
        ).json()
        return Workflow(**resp)

    def stop_workflow(self, namespace: str, name: str, req: WorkflowStopRequest) -> Workflow:
        resp = requests.put(
            url=os.path.join(self.host, "/api/v1/workflows/{namespace}/{name}/stop").format(
                namespace=namespace, name=name
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(),
            verify=self.verify_ssl,
        ).json()
        return Workflow(**resp)

    def suspend_workflow(self, namespace: str, name: str, req: WorkflowSuspendRequest) -> Workflow:
        resp = requests.put(
            url=os.path.join(self.host, "/api/v1/workflows/{namespace}/{name}/suspend").format(
                namespace=namespace, name=name
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(),
            verify=self.verify_ssl,
        ).json()
        return Workflow(**resp)

    def terminate_workflow(self, namespace: str, name: str, req: WorkflowTerminateRequest) -> Workflow:
        resp = requests.put(
            url=os.path.join(self.host, "/api/v1/workflows/{namespace}/{name}/terminate").format(
                namespace=namespace, name=name
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(),
            verify=self.verify_ssl,
        ).json()
        return Workflow(**resp)

    def pod_logs(
        self,
        namespace: str,
        name: str,
        pod_name: str,
        container: Optional[str] = None,
        follow: Optional[bool] = None,
        previous: Optional[bool] = None,
        since_seconds: Optional[str] = None,
        seconds: Optional[str] = None,
        nanos: Optional[int] = None,
        timestamps: Optional[bool] = None,
        tail_lines: Optional[str] = None,
        limit_bytes: Optional[str] = None,
        insecure_skip_tls_verify_backend: Optional[bool] = None,
        grep: Optional[str] = None,
        selector: Optional[str] = None,
    ) -> LogEntry:
        """DEPRECATED: Cannot work via HTTP if podName is an empty string. Use WorkflowLogs."""

        resp = requests.get(
            url=os.path.join(self.host, "/api/v1/workflows/{namespace}/{name}/{podName}/log").format(
                namespace=namespace, name=name, pod_name=pod_name
            ),
            params={
                "logOptions.container": container,
                "logOptions.follow": follow,
                "logOptions.previous": previous,
                "logOptions.sinceSeconds": since_seconds,
                "logOptions.sinceTime.seconds": seconds,
                "logOptions.sinceTime.nanos": nanos,
                "logOptions.timestamps": timestamps,
                "logOptions.tailLines": tail_lines,
                "logOptions.limitBytes": limit_bytes,
                "logOptions.insecureSkipTLSVerifyBackend": insecure_skip_tls_verify_backend,
                "grep": grep,
                "selector": selector,
            },
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        ).json()
        return LogEntry(**resp)

    def get_artifact_file(
        self,
        namespace: str,
        id_discriminator: str,
        id_: str,
        node_id: str,
        artifact_name: str,
        artifact_discriminator: str,
    ) -> str:
        """Get an artifact."""

        resp = requests.get(
            url=os.path.join(
                self.host,
                "/artifact-files/{namespace}/{idDiscriminator}/{id}/{nodeId}/{artifactDiscriminator}/{artifactName}",
            ).format(
                namespace=namespace,
                id_discriminator=id_discriminator,
                id_=id_,
                node_id=node_id,
                artifact_name=artifact_name,
                artifact_discriminator=artifact_discriminator,
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        ).json()
        return pickle.dump(resp)

    def get_output_artifact_by_uid(self, uid: str, node_id: str, artifact_name: str) -> str:
        """Get an output artifact by UID."""

        resp = requests.get(
            url=os.path.join(self.host, "/artifacts-by-uid/{uid}/{nodeId}/{artifactName}").format(
                uid=uid, node_id=node_id, artifact_name=artifact_name
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        ).json()
        return pickle.dump(resp)

    def get_output_artifact(self, namespace: str, name: str, node_id: str, artifact_name: str) -> str:
        """Get an output artifact."""

        resp = requests.get(
            url=os.path.join(self.host, "/artifacts/{namespace}/{name}/{nodeId}/{artifactName}").format(
                namespace=namespace, name=name, node_id=node_id, artifact_name=artifact_name
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        ).json()
        return pickle.dump(resp)

    def get_input_artifact_by_uid(self, uid: str, node_id: str, artifact_name: str) -> str:
        """Get an input artifact by UID."""

        resp = requests.get(
            url=os.path.join(self.host, "/input-artifacts-by-uid/{uid}/{nodeId}/{artifactName}").format(
                uid=uid, node_id=node_id, artifact_name=artifact_name
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        ).json()
        return pickle.dump(resp)

    def get_input_artifact(self, namespace: str, name: str, node_id: str, artifact_name: str) -> str:
        """Get an input artifact."""

        resp = requests.get(
            url=os.path.join(self.host, "/input-artifacts/{namespace}/{name}/{nodeId}/{artifactName}").format(
                namespace=namespace, name=name, node_id=node_id, artifact_name=artifact_name
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        ).json()
        return pickle.dump(resp)
