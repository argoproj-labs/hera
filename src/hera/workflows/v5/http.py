from typing import List, Optional

from hera.workflows.models import (
    HTTP as _ModelHTTP,
    HTTPBodySource,
    Template as _ModelTemplate,
    V1HTTPHeader as HTTPHeader,
)
from hera.workflows.v5._mixins import _SubNodeMixin, _TemplateMixin


class HTTP(_TemplateMixin, _SubNodeMixin):
    url: str
    body: Optional[str] = None
    body_from: Optional[HTTPBodySource] = None
    headers: Optional[List[HTTPHeader]] = None
    insecure_skip_verify: Optional[bool] = None
    method: Optional[str] = None
    success_condition: Optional[str] = None
    timeout_seconds: Optional[int] = None

    def _build_http_template(self) -> _ModelHTTP:
        return _ModelHTTP(
            url=self.url,
            body=self.body,
            body_from=self.body_from,
            headers=self.headers,
            insecure_skip_verify=self.insecure_skip_verify,
            method=self.method,
            success_condition=self.success_condition,
            timeout_seconds=self.timeout_seconds,
        )

    def _build_template(self) -> _ModelTemplate:
        return _ModelTemplate(
            active_deadline_seconds=self.active_deadline_seconds,
            affinity=self.affinity,
            archive_location=self.archive_location,
            automount_service_account_token=self.automount_service_account_token,
            container=None,
            container_set=None,
            daemon=self.daemon,
            dag=None,
            data=None,
            executor=self.executor,
            fail_fast=self.fail_fast,
            host_aliases=self.host_aliases,
            http=self._build_http_template(),
            init_containers=self.init_containers,
            inputs=None,
            memoize=self.memoize,
            metadata=self._build_metadata(),
            metrics=self.metrics,
            name=self.name,
            node_selector=self.node_selector,
            outputs=None,
            parallelism=self.paralellism,
            plugin=self.plugin,
            pod_spec_patch=self.pod_spec_patch,
            priority=self.priority,
            priority_class_name=self.priority_class_name,
            resource=None,
            retry_strategy=self.retry_strategy,
            scheduler_name=self.scheduler_name,
            script=None,
            security_context=self.pod_security_context,
            service_account_name=self.service_account_name,
            sidecars=self.sidecars,
            steps=None,
            suspend=None,
            synchronization=self.synchronization,
            timeout=self.timeout,
            tolerations=self.tolerations,
        )
