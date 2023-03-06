from typing import List

from hera.workflows.models import Data as _ModelData
from hera.workflows.models import DataSource
from hera.workflows.models import Template as _ModelTemplate
from hera.workflows.models import TransformationStep
from hera.workflows.v5._mixins import _SubNodeMixin, _TemplateMixin


class Data(_TemplateMixin, _SubNodeMixin):
    source: DataSource
    transformation: List[TransformationStep]

    def _build_data(self) -> _ModelData:
        return _ModelData(
            source=self.source,
            transformation=self.transformation,
        )

    def _build_template(self) -> _ModelTemplate:
        return _ModelTemplate(
            active_deadline_seconds=self.active_deadline_seconds,
            affinity=self.affinity,
            archive_location=self.archive_location,
            automount_service_account_token=self.automount_service_account_token,
            data=self._build_data(),
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
