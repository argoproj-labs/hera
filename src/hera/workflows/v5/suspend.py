from typing import Optional, Union

from hera.workflows.models import (
    SuspendTemplate as _ModelSuspendTemplate,
    Template as _ModelTemplate,
)
from hera.workflows.v5._mixins import _SubNodeMixin, _TemplateMixin


class Suspend(_TemplateMixin, _SubNodeMixin):
    duration: Optional[Union[int, str]] = None

    def _build_duration(self) -> str:
        return str(self.duration)

    def _build_suspend_template(self) -> _ModelSuspendTemplate:
        return _ModelSuspendTemplate(
            duration=self._build_duration(),
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
            init_containers=self.init_containers,
            memoize=self.memoize,
            metadata=self._build_metadata(),
            name=self.name,
            node_selector=self.node_selector,
            plugin=self.plugin,
            priority=self.priority,
            priority_class_name=self.priority_class_name,
            retry_strategy=self.retry_strategy,
            scheduler_name=self.scheduler_name,
            security_context=self.pod_security_context,
            service_account_name=self.service_account_name,
            sidecars=self.sidecars,
            synchronization=self.synchronization,
            timeout=self.timeout,
            tolerations=self.tolerations,
        )
