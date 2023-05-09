from typing import List, Optional

from hera.workflows._mixins import CallableTemplateMixin, IOMixin, TemplateMixin
from hera.workflows.models import (
    HTTP as _ModelHTTP,
    HTTPBodySource,
    Template as _ModelTemplate,
    V1HTTPHeader as HTTPHeader,
)


class HTTP(TemplateMixin, IOMixin, CallableTemplateMixin):
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
            executor=self.executor,
            fail_fast=self.fail_fast,
            host_aliases=self.host_aliases,
            http=self._build_http_template(),
            init_containers=self.init_containers,
            memoize=self.memoize,
            metadata=self._build_metadata(),
            inputs=self._build_inputs(),
            outputs=self._build_outputs(),
            name=self.name,
            node_selector=self.node_selector,
            plugin=self.plugin,
            priority=self.priority,
            priority_class_name=self.priority_class_name,
            retry_strategy=self.retry_strategy,
            scheduler_name=self.scheduler_name,
            security_context=self.pod_security_context,
            service_account_name=self.service_account_name,
            sidecars=self._build_sidecars(),
            synchronization=self.synchronization,
            timeout=self.timeout,
            tolerations=self.tolerations,
        )


__all__ = ["HTTP"]
