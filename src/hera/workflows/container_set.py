from __future__ import annotations

from typing import Any, List, Optional, Union

from hera.workflows._mixins import (
    ContainerMixin,
    ContextMixin,
    EnvIOMixin,
    ResourceMixin,
    SubNodeMixin,
    TemplateMixin,
    VolumeMountMixin,
)
from hera.workflows.exceptions import InvalidType
from hera.workflows.models import (
    ContainerNode as _ModelContainerNode,
    ContainerSetRetryStrategy,
    ContainerSetTemplate as _ModelContainerSetTemplate,
    Template as _ModelTemplate,
)


class ContainerNode(_ModelContainerNode, SubNodeMixin):
    def next(self, other: ContainerNode) -> ContainerNode:
        assert issubclass(other.__class__, ContainerNode)
        if other.dependencies is None:
            other.dependencies = [self.name]
        else:
            other.dependencies.append(self.name)
        other.dependencies = sorted(list(set(other.dependencies)))
        return other

    def __rrshift__(self, other: List[ContainerNode]) -> ContainerNode:
        assert isinstance(other, list), f"Unknown type {type(other)} specified using reverse right bitshift operator"
        for o in other:
            o.next(self)
        return self

    def __rshift__(
        self, other: Union[ContainerNode, List[ContainerNode]]
    ) -> Union[ContainerNode, List[ContainerNode]]:
        if isinstance(other, ContainerNode):
            return self.next(other)
        elif isinstance(other, list):
            for o in other:
                assert isinstance(
                    o, ContainerNode
                ), f"Unknown list item type {type(o)} specified using right bitshift operator `>>`"
                self.next(o)
            return other
        raise ValueError(f"Unknown type {type(other)} provided to `__rshift__`")


class ContainerSet(
    EnvIOMixin,
    ContainerMixin,
    TemplateMixin,
    ResourceMixin,
    VolumeMountMixin,
    ContextMixin,
):
    containers: List[ContainerNode] = []
    container_set_retry_strategy: Optional[ContainerSetRetryStrategy] = None

    def _add_sub(self, node: Any):
        if not isinstance(node, ContainerNode):
            raise InvalidType(type(node))

        self.containers.append(node)

    def _build_container_set(self) -> _ModelContainerSetTemplate:
        return _ModelContainerSetTemplate(
            containers=self.containers,
            retry_strategy=self.container_set_retry_strategy,
            volume_mounts=self.volume_mounts,
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


__all__ = ["ContainerNode", "ContainerSet"]
