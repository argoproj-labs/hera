from __future__ import annotations

from typing import List, Optional, Union

from hera.workflows._mixins import (
    ContainerMixin,
    EnvMixin,
    IOMixin,
    ResourceMixin,
    TemplateMixin,
    VolumeMountMixin,
)
from hera.workflows.container import Container
from hera.workflows.models import (
    ContainerNode,
    ContainerSetRetryStrategy,
    ContainerSetTemplate as _ModelContainerSetTemplate,
    Template as _ModelTemplate,
)
from hera.workflows.volume import Volume


class ContainerSet(
    IOMixin,
    ContainerMixin,
    EnvMixin,
    TemplateMixin,
    ResourceMixin,
    VolumeMountMixin,
):
    containers: List[Union[Container, ContainerNode]]
    retry_strategy: Optional[ContainerSetRetryStrategy] = None
    volume_mounts: Optional[List[Volume]] = None

    def _build_container_set(self) -> _ModelContainerSetTemplate:
        return _ModelContainerSetTemplate(
            containers=self.containers,
            retry_strategy=self.retry_strategy,
            volume_mounts=[v._build_volume_mount() for v in self.volume_mounts],
        )

    def _build_template(self) -> _ModelTemplate:
        return _ModelTemplate(
            active_deadline_seconds=self.active_deadline_seconds,
            affinity=self.affinity,
            archive_location=self.archive_location,
            automount_service_account_token=self.automount_service_account_token,
            container_set=self._build_container_set(),
            daemon=self.daemon,
            executor=self.executor,
            fail_fast=self.fail_fast,
            host_aliases=self.host_aliases,
            init_containers=self.init_containers,
            inputs=self._build_inputs(),
            memoize=self.memoize,
            metadata=self._build_metadata(),
            metrics=self.metrics,
            name=self.name,
            node_selector=self.node_selector,
            outputs=self._build_outputs(),
            plugin=self.plugin,
            pod_spec_patch=self.pod_spec_patch,
            priority=self.priority,
            priority_class_name=self.priority_class_name,
            resource=self._build_resources(),
            retry_strategy=self.retry_strategy,
            scheduler_name=self.scheduler_name,
            security_context=self.pod_security_context,
            service_account_name=self.service_account_name,
            sidecars=self.sidecars,
            synchronization=self.synchronization,
            timeout=self.timeout,
            tolerations=self.tolerations,
            volumes=self._build_volumes(),
        )
