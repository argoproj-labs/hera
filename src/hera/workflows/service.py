from typing import Optional, cast
from urllib.parse import urljoin

import requests

from hera.exceptions import exception_from_server_response
from hera.shared import global_config
from hera.workflows.models import (
    ArchivedWorkflowDeletedResponse,
    ClusterWorkflowTemplate,
    ClusterWorkflowTemplateCreateRequest,
    ClusterWorkflowTemplateDeleteResponse,
    ClusterWorkflowTemplateLintRequest,
    ClusterWorkflowTemplateList,
    ClusterWorkflowTemplateUpdateRequest,
    CreateCronWorkflowRequest,
    CronWorkflow,
    CronWorkflowDeletedResponse,
    CronWorkflowList,
    CronWorkflowResumeRequest,
    CronWorkflowSuspendRequest,
    GetUserInfoResponse,
    InfoResponse,
    LabelKeys,
    LabelValues,
    LintCronWorkflowRequest,
    ResubmitArchivedWorkflowRequest,
    RetryArchivedWorkflowRequest,
    UpdateCronWorkflowRequest,
    V1alpha1LogEntry,
    Version,
    Workflow,
    WorkflowCreateRequest,
    WorkflowDeleteResponse,
    WorkflowLintRequest,
    WorkflowList,
    WorkflowResubmitRequest,
    WorkflowResumeRequest,
    WorkflowRetryRequest,
    WorkflowSetRequest,
    WorkflowStopRequest,
    WorkflowSubmitRequest,
    WorkflowSuspendRequest,
    WorkflowTemplate,
    WorkflowTemplateCreateRequest,
    WorkflowTemplateDeleteResponse,
    WorkflowTemplateLintRequest,
    WorkflowTemplateList,
    WorkflowTemplateUpdateRequest,
    WorkflowTerminateRequest,
)


def valid_host_scheme(host: str) -> bool:
    return host.startswith("http://") or host.startswith("https://")


class WorkflowsService:
    def __init__(
        self,
        host: Optional[str] = None,
        verify_ssl: Optional[bool] = None,
        token: Optional[str] = None,
        namespace: Optional[str] = None,
    ):
        self.host = cast(str, host or global_config.host)
        self.verify_ssl = verify_ssl if verify_ssl is not None else global_config.verify_ssl
        self.token = token or global_config.token
        self.namespace = namespace or global_config.namespace

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
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.get(
            url=urljoin(self.host, "api/v1/archived-workflows"),
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
        )

        if resp.ok:
            return WorkflowList(**resp.json())

        raise exception_from_server_response(resp)

    def list_archived_workflow_label_keys(self) -> LabelKeys:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.get(
            url=urljoin(self.host, "api/v1/archived-workflows-label-keys"),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        )

        if resp.ok:
            return LabelKeys(**resp.json())

        raise exception_from_server_response(resp)

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
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.get(
            url=urljoin(self.host, "api/v1/archived-workflows-label-values"),
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
        )

        if resp.ok:
            return LabelValues(**resp.json())

        raise exception_from_server_response(resp)

    def get_archived_workflow(self, uid: str) -> Workflow:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.get(
            url=urljoin(self.host, "api/v1/archived-workflows/{uid}").format(uid=uid),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        )

        if resp.ok:
            return Workflow(**resp.json())

        raise exception_from_server_response(resp)

    def delete_archived_workflow(self, uid: str) -> ArchivedWorkflowDeletedResponse:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.delete(
            url=urljoin(self.host, "api/v1/archived-workflows/{uid}").format(uid=uid),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        )

        if resp.ok:
            return ArchivedWorkflowDeletedResponse()

        raise exception_from_server_response(resp)

    def resubmit_archived_workflow(self, uid: str, req: ResubmitArchivedWorkflowRequest) -> Workflow:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.put(
            url=urljoin(self.host, "api/v1/archived-workflows/{uid}/resubmit").format(uid=uid),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(
                exclude_none=True, by_alias=True, skip_defaults=True, exclude_unset=True, exclude_defaults=True
            ),
            verify=self.verify_ssl,
        )

        if resp.ok:
            return Workflow(**resp.json())

        raise exception_from_server_response(resp)

    def retry_archived_workflow(self, uid: str, req: RetryArchivedWorkflowRequest) -> Workflow:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.put(
            url=urljoin(self.host, "api/v1/archived-workflows/{uid}/retry").format(uid=uid),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(
                exclude_none=True, by_alias=True, skip_defaults=True, exclude_unset=True, exclude_defaults=True
            ),
            verify=self.verify_ssl,
        )

        if resp.ok:
            return Workflow(**resp.json())

        raise exception_from_server_response(resp)

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
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.get(
            url=urljoin(self.host, "api/v1/cluster-workflow-templates"),
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
        )

        if resp.ok:
            return ClusterWorkflowTemplateList(**resp.json())

        raise exception_from_server_response(resp)

    def create_cluster_workflow_template(self, req: ClusterWorkflowTemplateCreateRequest) -> ClusterWorkflowTemplate:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.post(
            url=urljoin(self.host, "api/v1/cluster-workflow-templates"),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(
                exclude_none=True, by_alias=True, skip_defaults=True, exclude_unset=True, exclude_defaults=True
            ),
            verify=self.verify_ssl,
        )

        if resp.ok:
            return ClusterWorkflowTemplate(**resp.json())

        raise exception_from_server_response(resp)

    def lint_cluster_workflow_template(self, req: ClusterWorkflowTemplateLintRequest) -> ClusterWorkflowTemplate:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.post(
            url=urljoin(self.host, "api/v1/cluster-workflow-templates/lint"),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(
                exclude_none=True, by_alias=True, skip_defaults=True, exclude_unset=True, exclude_defaults=True
            ),
            verify=self.verify_ssl,
        )

        if resp.ok:
            return ClusterWorkflowTemplate(**resp.json())

        raise exception_from_server_response(resp)

    def get_cluster_workflow_template(
        self, name: str, resource_version: Optional[str] = None
    ) -> ClusterWorkflowTemplate:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.get(
            url=urljoin(self.host, "api/v1/cluster-workflow-templates/{name}").format(name=name),
            params={"getOptions.resourceVersion": resource_version},
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        )

        if resp.ok:
            return ClusterWorkflowTemplate(**resp.json())

        raise exception_from_server_response(resp)

    def update_cluster_workflow_template(
        self, name: str, req: ClusterWorkflowTemplateUpdateRequest
    ) -> ClusterWorkflowTemplate:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.put(
            url=urljoin(self.host, "api/v1/cluster-workflow-templates/{name}").format(name=name),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(
                exclude_none=True, by_alias=True, skip_defaults=True, exclude_unset=True, exclude_defaults=True
            ),
            verify=self.verify_ssl,
        )

        if resp.ok:
            return ClusterWorkflowTemplate(**resp.json())

        raise exception_from_server_response(resp)

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
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.delete(
            url=urljoin(self.host, "api/v1/cluster-workflow-templates/{name}").format(name=name),
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
        )

        if resp.ok:
            return ClusterWorkflowTemplateDeleteResponse()

        raise exception_from_server_response(resp)

    def list_cron_workflows(
        self,
        namespace: Optional[str] = None,
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
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.get(
            url=urljoin(self.host, "api/v1/cron-workflows/{namespace}").format(
                namespace=namespace if namespace is not None else self.namespace
            ),
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
        )

        if resp.ok:
            resp_json = resp.json()
            if (
                "status" in resp_json
                and resp_json["status"]["active"] is None
                and resp_json["status"]["lastScheduledTime"] is None
                and resp_json["status"]["conditions"] is None
            ):
                # this is a necessary special case as the status fields cannot be empty on the `CronWorkflowStatus`
                # object. So, we overwrite the response with a value that allows the response to pass through safely.
                # See `hera.scripts.service.ServiceEndpoint.__str__` for more details.
                resp_json["status"] = None
            return CronWorkflowList(**resp_json)

        raise exception_from_server_response(resp)

    def create_cron_workflow(self, req: CreateCronWorkflowRequest, namespace: Optional[str] = None) -> CronWorkflow:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.post(
            url=urljoin(self.host, "api/v1/cron-workflows/{namespace}").format(
                namespace=namespace if namespace is not None else self.namespace
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(
                exclude_none=True, by_alias=True, skip_defaults=True, exclude_unset=True, exclude_defaults=True
            ),
            verify=self.verify_ssl,
        )

        if resp.ok:
            resp_json = resp.json()
            if (
                "status" in resp_json
                and resp_json["status"]["active"] is None
                and resp_json["status"]["lastScheduledTime"] is None
                and resp_json["status"]["conditions"] is None
            ):
                # this is a necessary special case as the status fields cannot be empty on the `CronWorkflowStatus`
                # object. So, we overwrite the response with a value that allows the response to pass through safely.
                # See `hera.scripts.service.ServiceEndpoint.__str__` for more details.
                resp_json["status"] = None
            return CronWorkflow(**resp_json)

        raise exception_from_server_response(resp)

    def lint_cron_workflow(self, req: LintCronWorkflowRequest, namespace: Optional[str] = None) -> CronWorkflow:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.post(
            url=urljoin(self.host, "api/v1/cron-workflows/{namespace}/lint").format(
                namespace=namespace if namespace is not None else self.namespace
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(
                exclude_none=True, by_alias=True, skip_defaults=True, exclude_unset=True, exclude_defaults=True
            ),
            verify=self.verify_ssl,
        )

        if resp.ok:
            resp_json = resp.json()
            if (
                "status" in resp_json
                and resp_json["status"]["active"] is None
                and resp_json["status"]["lastScheduledTime"] is None
                and resp_json["status"]["conditions"] is None
            ):
                # this is a necessary special case as the status fields cannot be empty on the `CronWorkflowStatus`
                # object. So, we overwrite the response with a value that allows the response to pass through safely.
                # See `hera.scripts.service.ServiceEndpoint.__str__` for more details.
                resp_json["status"] = None
            return CronWorkflow(**resp_json)

        raise exception_from_server_response(resp)

    def get_cron_workflow(
        self, name: str, namespace: Optional[str] = None, resource_version: Optional[str] = None
    ) -> CronWorkflow:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.get(
            url=urljoin(self.host, "api/v1/cron-workflows/{namespace}/{name}").format(
                name=name, namespace=namespace if namespace is not None else self.namespace
            ),
            params={"getOptions.resourceVersion": resource_version},
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        )

        if resp.ok:
            resp_json = resp.json()
            if (
                "status" in resp_json
                and resp_json["status"]["active"] is None
                and resp_json["status"]["lastScheduledTime"] is None
                and resp_json["status"]["conditions"] is None
            ):
                # this is a necessary special case as the status fields cannot be empty on the `CronWorkflowStatus`
                # object. So, we overwrite the response with a value that allows the response to pass through safely.
                # See `hera.scripts.service.ServiceEndpoint.__str__` for more details.
                resp_json["status"] = None
            return CronWorkflow(**resp_json)

        raise exception_from_server_response(resp)

    def update_cron_workflow(
        self, name: str, req: UpdateCronWorkflowRequest, namespace: Optional[str] = None
    ) -> CronWorkflow:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.put(
            url=urljoin(self.host, "api/v1/cron-workflows/{namespace}/{name}").format(
                name=name, namespace=namespace if namespace is not None else self.namespace
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(
                exclude_none=True, by_alias=True, skip_defaults=True, exclude_unset=True, exclude_defaults=True
            ),
            verify=self.verify_ssl,
        )

        if resp.ok:
            resp_json = resp.json()
            if (
                "status" in resp_json
                and resp_json["status"]["active"] is None
                and resp_json["status"]["lastScheduledTime"] is None
                and resp_json["status"]["conditions"] is None
            ):
                # this is a necessary special case as the status fields cannot be empty on the `CronWorkflowStatus`
                # object. So, we overwrite the response with a value that allows the response to pass through safely.
                # See `hera.scripts.service.ServiceEndpoint.__str__` for more details.
                resp_json["status"] = None
            return CronWorkflow(**resp_json)

        raise exception_from_server_response(resp)

    def delete_cron_workflow(
        self,
        name: str,
        namespace: Optional[str] = None,
        grace_period_seconds: Optional[str] = None,
        uid: Optional[str] = None,
        resource_version: Optional[str] = None,
        orphan_dependents: Optional[bool] = None,
        propagation_policy: Optional[str] = None,
        dry_run: Optional[list] = None,
    ) -> CronWorkflowDeletedResponse:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.delete(
            url=urljoin(self.host, "api/v1/cron-workflows/{namespace}/{name}").format(
                name=name, namespace=namespace if namespace is not None else self.namespace
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
        )

        if resp.ok:
            return CronWorkflowDeletedResponse()

        raise exception_from_server_response(resp)

    def resume_cron_workflow(
        self, name: str, req: CronWorkflowResumeRequest, namespace: Optional[str] = None
    ) -> CronWorkflow:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.put(
            url=urljoin(self.host, "api/v1/cron-workflows/{namespace}/{name}/resume").format(
                name=name, namespace=namespace if namespace is not None else self.namespace
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(
                exclude_none=True, by_alias=True, skip_defaults=True, exclude_unset=True, exclude_defaults=True
            ),
            verify=self.verify_ssl,
        )

        if resp.ok:
            resp_json = resp.json()
            if (
                "status" in resp_json
                and resp_json["status"]["active"] is None
                and resp_json["status"]["lastScheduledTime"] is None
                and resp_json["status"]["conditions"] is None
            ):
                # this is a necessary special case as the status fields cannot be empty on the `CronWorkflowStatus`
                # object. So, we overwrite the response with a value that allows the response to pass through safely.
                # See `hera.scripts.service.ServiceEndpoint.__str__` for more details.
                resp_json["status"] = None
            return CronWorkflow(**resp_json)

        raise exception_from_server_response(resp)

    def suspend_cron_workflow(
        self, name: str, req: CronWorkflowSuspendRequest, namespace: Optional[str] = None
    ) -> CronWorkflow:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.put(
            url=urljoin(self.host, "api/v1/cron-workflows/{namespace}/{name}/suspend").format(
                name=name, namespace=namespace if namespace is not None else self.namespace
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(
                exclude_none=True, by_alias=True, skip_defaults=True, exclude_unset=True, exclude_defaults=True
            ),
            verify=self.verify_ssl,
        )

        if resp.ok:
            resp_json = resp.json()
            if (
                "status" in resp_json
                and resp_json["status"]["active"] is None
                and resp_json["status"]["lastScheduledTime"] is None
                and resp_json["status"]["conditions"] is None
            ):
                # this is a necessary special case as the status fields cannot be empty on the `CronWorkflowStatus`
                # object. So, we overwrite the response with a value that allows the response to pass through safely.
                # See `hera.scripts.service.ServiceEndpoint.__str__` for more details.
                resp_json["status"] = None
            return CronWorkflow(**resp_json)

        raise exception_from_server_response(resp)

    def get_info(self) -> InfoResponse:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.get(
            url=urljoin(self.host, "api/v1/info"),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        )

        if resp.ok:
            return InfoResponse()

        raise exception_from_server_response(resp)

    def get_user_info(self) -> GetUserInfoResponse:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.get(
            url=urljoin(self.host, "api/v1/userinfo"),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        )

        if resp.ok:
            return GetUserInfoResponse()

        raise exception_from_server_response(resp)

    def get_version(self) -> Version:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.get(
            url=urljoin(self.host, "api/v1/version"),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        )

        if resp.ok:
            return Version(**resp.json())

        raise exception_from_server_response(resp)

    def list_workflow_templates(
        self,
        namespace: Optional[str] = None,
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
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.get(
            url=urljoin(self.host, "api/v1/workflow-templates/{namespace}").format(
                namespace=namespace if namespace is not None else self.namespace
            ),
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
        )

        if resp.ok:
            return WorkflowTemplateList(**resp.json())

        raise exception_from_server_response(resp)

    def create_workflow_template(
        self, req: WorkflowTemplateCreateRequest, namespace: Optional[str] = None
    ) -> WorkflowTemplate:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.post(
            url=urljoin(self.host, "api/v1/workflow-templates/{namespace}").format(
                namespace=namespace if namespace is not None else self.namespace
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(
                exclude_none=True, by_alias=True, skip_defaults=True, exclude_unset=True, exclude_defaults=True
            ),
            verify=self.verify_ssl,
        )

        if resp.ok:
            return WorkflowTemplate(**resp.json())

        raise exception_from_server_response(resp)

    def lint_workflow_template(
        self, req: WorkflowTemplateLintRequest, namespace: Optional[str] = None
    ) -> WorkflowTemplate:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.post(
            url=urljoin(self.host, "api/v1/workflow-templates/{namespace}/lint").format(
                namespace=namespace if namespace is not None else self.namespace
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(
                exclude_none=True, by_alias=True, skip_defaults=True, exclude_unset=True, exclude_defaults=True
            ),
            verify=self.verify_ssl,
        )

        if resp.ok:
            return WorkflowTemplate(**resp.json())

        raise exception_from_server_response(resp)

    def get_workflow_template(
        self, name: str, namespace: Optional[str] = None, resource_version: Optional[str] = None
    ) -> WorkflowTemplate:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.get(
            url=urljoin(self.host, "api/v1/workflow-templates/{namespace}/{name}").format(
                name=name, namespace=namespace if namespace is not None else self.namespace
            ),
            params={"getOptions.resourceVersion": resource_version},
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        )

        if resp.ok:
            return WorkflowTemplate(**resp.json())

        raise exception_from_server_response(resp)

    def update_workflow_template(
        self, name: str, req: WorkflowTemplateUpdateRequest, namespace: Optional[str] = None
    ) -> WorkflowTemplate:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.put(
            url=urljoin(self.host, "api/v1/workflow-templates/{namespace}/{name}").format(
                name=name, namespace=namespace if namespace is not None else self.namespace
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(
                exclude_none=True, by_alias=True, skip_defaults=True, exclude_unset=True, exclude_defaults=True
            ),
            verify=self.verify_ssl,
        )

        if resp.ok:
            return WorkflowTemplate(**resp.json())

        raise exception_from_server_response(resp)

    def delete_workflow_template(
        self,
        name: str,
        namespace: Optional[str] = None,
        grace_period_seconds: Optional[str] = None,
        uid: Optional[str] = None,
        resource_version: Optional[str] = None,
        orphan_dependents: Optional[bool] = None,
        propagation_policy: Optional[str] = None,
        dry_run: Optional[list] = None,
    ) -> WorkflowTemplateDeleteResponse:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.delete(
            url=urljoin(self.host, "api/v1/workflow-templates/{namespace}/{name}").format(
                name=name, namespace=namespace if namespace is not None else self.namespace
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
        )

        if resp.ok:
            return WorkflowTemplateDeleteResponse()

        raise exception_from_server_response(resp)

    def list_workflows(
        self,
        namespace: Optional[str] = None,
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
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.get(
            url=urljoin(self.host, "api/v1/workflows/{namespace}").format(
                namespace=namespace if namespace is not None else self.namespace
            ),
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
        )

        if resp.ok:
            return WorkflowList(**resp.json())

        raise exception_from_server_response(resp)

    def create_workflow(self, req: WorkflowCreateRequest, namespace: Optional[str] = None) -> Workflow:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.post(
            url=urljoin(self.host, "api/v1/workflows/{namespace}").format(
                namespace=namespace if namespace is not None else self.namespace
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(
                exclude_none=True, by_alias=True, skip_defaults=True, exclude_unset=True, exclude_defaults=True
            ),
            verify=self.verify_ssl,
        )

        if resp.ok:
            return Workflow(**resp.json())

        raise exception_from_server_response(resp)

    def lint_workflow(self, req: WorkflowLintRequest, namespace: Optional[str] = None) -> Workflow:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.post(
            url=urljoin(self.host, "api/v1/workflows/{namespace}/lint").format(
                namespace=namespace if namespace is not None else self.namespace
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(
                exclude_none=True, by_alias=True, skip_defaults=True, exclude_unset=True, exclude_defaults=True
            ),
            verify=self.verify_ssl,
        )

        if resp.ok:
            return Workflow(**resp.json())

        raise exception_from_server_response(resp)

    def submit_workflow(self, req: WorkflowSubmitRequest, namespace: Optional[str] = None) -> Workflow:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.post(
            url=urljoin(self.host, "api/v1/workflows/{namespace}/submit").format(
                namespace=namespace if namespace is not None else self.namespace
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(
                exclude_none=True, by_alias=True, skip_defaults=True, exclude_unset=True, exclude_defaults=True
            ),
            verify=self.verify_ssl,
        )

        if resp.ok:
            return Workflow(**resp.json())

        raise exception_from_server_response(resp)

    def get_workflow(
        self,
        name: str,
        namespace: Optional[str] = None,
        resource_version: Optional[str] = None,
        fields: Optional[str] = None,
    ) -> Workflow:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.get(
            url=urljoin(self.host, "api/v1/workflows/{namespace}/{name}").format(
                name=name, namespace=namespace if namespace is not None else self.namespace
            ),
            params={"getOptions.resourceVersion": resource_version, "fields": fields},
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        )

        if resp.ok:
            return Workflow(**resp.json())

        raise exception_from_server_response(resp)

    def delete_workflow(
        self,
        name: str,
        namespace: Optional[str] = None,
        grace_period_seconds: Optional[str] = None,
        uid: Optional[str] = None,
        resource_version: Optional[str] = None,
        orphan_dependents: Optional[bool] = None,
        propagation_policy: Optional[str] = None,
        dry_run: Optional[list] = None,
        force: Optional[bool] = None,
    ) -> WorkflowDeleteResponse:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.delete(
            url=urljoin(self.host, "api/v1/workflows/{namespace}/{name}").format(
                name=name, namespace=namespace if namespace is not None else self.namespace
            ),
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
        )

        if resp.ok:
            return WorkflowDeleteResponse()

        raise exception_from_server_response(resp)

    def workflow_logs(
        self,
        name: str,
        namespace: Optional[str] = None,
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
    ) -> V1alpha1LogEntry:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.get(
            url=urljoin(self.host, "api/v1/workflows/{namespace}/{name}/log").format(
                name=name, namespace=namespace if namespace is not None else self.namespace
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
        )

        if resp.ok:
            return V1alpha1LogEntry(**resp.json())

        raise exception_from_server_response(resp)

    def resubmit_workflow(self, name: str, req: WorkflowResubmitRequest, namespace: Optional[str] = None) -> Workflow:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.put(
            url=urljoin(self.host, "api/v1/workflows/{namespace}/{name}/resubmit").format(
                name=name, namespace=namespace if namespace is not None else self.namespace
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(
                exclude_none=True, by_alias=True, skip_defaults=True, exclude_unset=True, exclude_defaults=True
            ),
            verify=self.verify_ssl,
        )

        if resp.ok:
            return Workflow(**resp.json())

        raise exception_from_server_response(resp)

    def resume_workflow(self, name: str, req: WorkflowResumeRequest, namespace: Optional[str] = None) -> Workflow:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.put(
            url=urljoin(self.host, "api/v1/workflows/{namespace}/{name}/resume").format(
                name=name, namespace=namespace if namespace is not None else self.namespace
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(
                exclude_none=True, by_alias=True, skip_defaults=True, exclude_unset=True, exclude_defaults=True
            ),
            verify=self.verify_ssl,
        )

        if resp.ok:
            return Workflow(**resp.json())

        raise exception_from_server_response(resp)

    def retry_workflow(self, name: str, req: WorkflowRetryRequest, namespace: Optional[str] = None) -> Workflow:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.put(
            url=urljoin(self.host, "api/v1/workflows/{namespace}/{name}/retry").format(
                name=name, namespace=namespace if namespace is not None else self.namespace
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(
                exclude_none=True, by_alias=True, skip_defaults=True, exclude_unset=True, exclude_defaults=True
            ),
            verify=self.verify_ssl,
        )

        if resp.ok:
            return Workflow(**resp.json())

        raise exception_from_server_response(resp)

    def set_workflow(self, name: str, req: WorkflowSetRequest, namespace: Optional[str] = None) -> Workflow:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.put(
            url=urljoin(self.host, "api/v1/workflows/{namespace}/{name}/set").format(
                name=name, namespace=namespace if namespace is not None else self.namespace
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(
                exclude_none=True, by_alias=True, skip_defaults=True, exclude_unset=True, exclude_defaults=True
            ),
            verify=self.verify_ssl,
        )

        if resp.ok:
            return Workflow(**resp.json())

        raise exception_from_server_response(resp)

    def stop_workflow(self, name: str, req: WorkflowStopRequest, namespace: Optional[str] = None) -> Workflow:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.put(
            url=urljoin(self.host, "api/v1/workflows/{namespace}/{name}/stop").format(
                name=name, namespace=namespace if namespace is not None else self.namespace
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(
                exclude_none=True, by_alias=True, skip_defaults=True, exclude_unset=True, exclude_defaults=True
            ),
            verify=self.verify_ssl,
        )

        if resp.ok:
            return Workflow(**resp.json())

        raise exception_from_server_response(resp)

    def suspend_workflow(self, name: str, req: WorkflowSuspendRequest, namespace: Optional[str] = None) -> Workflow:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.put(
            url=urljoin(self.host, "api/v1/workflows/{namespace}/{name}/suspend").format(
                name=name, namespace=namespace if namespace is not None else self.namespace
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(
                exclude_none=True, by_alias=True, skip_defaults=True, exclude_unset=True, exclude_defaults=True
            ),
            verify=self.verify_ssl,
        )

        if resp.ok:
            return Workflow(**resp.json())

        raise exception_from_server_response(resp)

    def terminate_workflow(
        self, name: str, req: WorkflowTerminateRequest, namespace: Optional[str] = None
    ) -> Workflow:
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.put(
            url=urljoin(self.host, "api/v1/workflows/{namespace}/{name}/terminate").format(
                name=name, namespace=namespace if namespace is not None else self.namespace
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=req.json(
                exclude_none=True, by_alias=True, skip_defaults=True, exclude_unset=True, exclude_defaults=True
            ),
            verify=self.verify_ssl,
        )

        if resp.ok:
            return Workflow(**resp.json())

        raise exception_from_server_response(resp)

    def pod_logs(
        self,
        name: str,
        pod_name: str,
        namespace: Optional[str] = None,
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
    ) -> V1alpha1LogEntry:
        """DEPRECATED: Cannot work via HTTP if podName is an empty string. Use WorkflowLogs."""
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.get(
            url=urljoin(self.host, "api/v1/workflows/{namespace}/{name}/{podName}/log").format(
                name=name, podName=pod_name, namespace=namespace if namespace is not None else self.namespace
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
        )

        if resp.ok:
            return V1alpha1LogEntry(**resp.json())

        raise exception_from_server_response(resp)

    def get_artifact_file(
        self,
        id_discriminator: str,
        id_: str,
        node_id: str,
        artifact_name: str,
        artifact_discriminator: str,
        namespace: Optional[str] = None,
    ) -> str:
        """Get an artifact."""
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.get(
            url=urljoin(
                self.host,
                "artifact-files/{namespace}/{idDiscriminator}/{id}/{nodeId}/{artifactDiscriminator}/{artifactName}",
            ).format(
                idDiscriminator=id_discriminator,
                id=id_,
                nodeId=node_id,
                artifactName=artifact_name,
                artifactDiscriminator=artifact_discriminator,
                namespace=namespace if namespace is not None else self.namespace,
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        )

        if resp.ok:
            return str(resp.content)

        raise exception_from_server_response(resp)

    def get_output_artifact_by_uid(self, uid: str, node_id: str, artifact_name: str) -> str:
        """Get an output artifact by UID."""
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.get(
            url=urljoin(self.host, "artifacts-by-uid/{uid}/{nodeId}/{artifactName}").format(
                uid=uid, nodeId=node_id, artifactName=artifact_name
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        )

        if resp.ok:
            return str(resp.content)

        raise exception_from_server_response(resp)

    def get_output_artifact(self, name: str, node_id: str, artifact_name: str, namespace: Optional[str] = None) -> str:
        """Get an output artifact."""
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.get(
            url=urljoin(self.host, "artifacts/{namespace}/{name}/{nodeId}/{artifactName}").format(
                name=name,
                nodeId=node_id,
                artifactName=artifact_name,
                namespace=namespace if namespace is not None else self.namespace,
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        )

        if resp.ok:
            return str(resp.content)

        raise exception_from_server_response(resp)

    def get_input_artifact_by_uid(self, uid: str, node_id: str, artifact_name: str) -> str:
        """Get an input artifact by UID."""
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.get(
            url=urljoin(self.host, "input-artifacts-by-uid/{uid}/{nodeId}/{artifactName}").format(
                uid=uid, nodeId=node_id, artifactName=artifact_name
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        )

        if resp.ok:
            return str(resp.content)

        raise exception_from_server_response(resp)

    def get_input_artifact(self, name: str, node_id: str, artifact_name: str, namespace: Optional[str] = None) -> str:
        """Get an input artifact."""
        assert valid_host_scheme(self.host), "The host scheme is required for service usage"
        resp = requests.get(
            url=urljoin(self.host, "input-artifacts/{namespace}/{name}/{nodeId}/{artifactName}").format(
                name=name,
                nodeId=node_id,
                artifactName=artifact_name,
                namespace=namespace if namespace is not None else self.namespace,
            ),
            params=None,
            headers={"Authorization": f"Bearer {self.token}"},
            data=None,
            verify=self.verify_ssl,
        )

        if resp.ok:
            return str(resp.content)

        raise exception_from_server_response(resp)


__all__ = ["WorkflowsService"]
