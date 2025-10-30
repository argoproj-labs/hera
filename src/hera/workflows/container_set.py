"""The `hera.workflows.container_set` module provides Argo's container set and container node."""

from __future__ import annotations

from typing import Any, List, Optional, Union

from hera.workflows._meta_mixins import CallableTemplateMixin, ContextMixin
from hera.workflows._mixins import (
    ContainerMixin,
    EnvIOMixin,
    EnvMixin,
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
    Lifecycle,
    SecurityContext,
    Template as _ModelTemplate,
)


class ContainerNode(ContainerMixin, VolumeMountMixin, ResourceMixin, EnvMixin, SubNodeMixin):
    """A regular container that can be used as part of a `hera.workflows.ContainerSet`.

    See Also:
        [Container Set Template](https://argoproj.github.io/argo-workflows/container-set-template/)
    """

    name: str
    args: Optional[List[str]] = None
    command: Optional[List[str]] = None
    dependencies: Optional[List[str]] = None
    lifecycle: Optional[Lifecycle] = None
    security_context: Optional[SecurityContext] = None
    working_dir: Optional[str] = None

    def next(self, other: ContainerNode) -> ContainerNode:
        """Sets the given container as a dependency of this container and returns the given container.

        Examples:
            >>> from hera.workflows import ContainerNode
            >>> a, b = ContainerNode(name="a"), ContainerNode(name="b")
            >>> a.next(b)
            >>> b.dependencies
            ['a']
        """
        assert issubclass(other.__class__, ContainerNode)
        if other.dependencies is None:
            other.dependencies = [self.name]
        else:
            other.dependencies.append(self.name)
        other.dependencies = sorted(list(set(other.dependencies)))
        return other

    def __rrshift__(self, other: List[ContainerNode]) -> ContainerNode:
        """Sets `self` as a dependent of the given list of other `hera.workflows.ContainerNode`.

        Practically, the `__rrshift__` allows us to express statements such as `[a, b, c] >> d`, where `d` is `self.`

        Examples:
            >>> from hera.workflows import ContainerNode
            >>> a, b, c = ContainerNode(name="a"), ContainerNode(name="b"), ContainerNode(name="c")
            >>> [a, b] >> c
            >>> c.dependencies
            ['a', 'b']
        """
        assert isinstance(other, list), f"Unknown type {type(other)} specified using reverse right bitshift operator"
        for o in other:
            o.next(self)
        return self

    def __rshift__(
        self, other: Union[ContainerNode, List[ContainerNode]]
    ) -> Union[ContainerNode, List[ContainerNode]]:
        """Sets the given container as a dependency of this container and returns the given container.

        Examples:
            >>> from hera.workflows import ContainerNode
            >>> a, b = ContainerNode(name="a"), ContainerNode(name="b")
            >>> a >> b
            >>> b.dependencies
            ['a']
        """
        if isinstance(other, ContainerNode):
            return self.next(other)
        elif isinstance(other, list):
            for o in other:
                assert isinstance(o, ContainerNode), (
                    f"Unknown list item type {type(o)} specified using right bitshift operator `>>`"
                )
                self.next(o)
            return other
        raise ValueError(f"Unknown type {type(other)} provided to `__rshift__`")

    def _build_container_node(self) -> _ModelContainerNode:
        """Builds the generated `ContainerNode`."""
        return _ModelContainerNode(
            args=self.args,
            command=self.command,
            dependencies=self.dependencies,
            env=self._build_env(),
            env_from=self._build_env_from(),
            image=self.image,
            image_pull_policy=self._build_image_pull_policy(),
            lifecycle=self.lifecycle,
            liveness_probe=self.liveness_probe,
            name=self.name,
            ports=self.ports,
            readiness_probe=self.readiness_probe,
            resize_policy=self.resize_policy,
            resources=self._build_resources(),
            restart_policy=self.restart_policy,
            security_context=self.security_context,
            startup_probe=self.startup_probe,
            stdin=self.stdin,
            stdin_once=self.stdin_once,
            termination_message_path=self.termination_message_path,
            termination_message_policy=self.termination_message_policy,
            tty=self.tty,
            volume_devices=self.volume_devices,
            volume_mounts=self._build_volume_mounts(),
            working_dir=self.working_dir,
        )


class ContainerSet(
    EnvIOMixin,
    ContainerMixin,
    TemplateMixin,
    CallableTemplateMixin,
    VolumeMountMixin,
    ContextMixin,
):
    """`ContainerSet` is the implementation of a set of containers that can be run in parallel on Kubernetes.

    The containers are run within the same pod.

    Examples:
        >>> with ContainerSet(...) as cs:
        >>>     ContainerNode(...)
        >>>     ContainerNode(...)
    """

    containers: List[Union[ContainerNode, _ModelContainerNode]] = []
    container_set_retry_strategy: Optional[ContainerSetRetryStrategy] = None

    def _add_sub(self, node: Any):
        if not isinstance(node, ContainerNode):
            raise InvalidType(type(node))

        self.containers.append(node)

    def _build_container_set(self) -> _ModelContainerSetTemplate:
        """Builds the generated `ContainerSetTemplate`."""
        containers = [c._build_container_node() if isinstance(c, ContainerNode) else c for c in self.containers]
        return _ModelContainerSetTemplate(
            containers=containers,
            retry_strategy=self.container_set_retry_strategy,
            volume_mounts=self.volume_mounts,
        )

    def _build_template(self) -> _ModelTemplate:
        """Builds the generated `Template` representation of the container set."""
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
            init_containers=self._build_init_containers(),
            inputs=self._build_inputs(),
            memoize=self.memoize,
            metadata=self._build_metadata(),
            metrics=self._build_metrics(),
            name=self.name,
            node_selector=self.node_selector,
            outputs=self._build_outputs(),
            plugin=self.plugin,
            pod_spec_patch=self.pod_spec_patch,
            priority_class_name=self.priority_class_name,
            retry_strategy=self._build_retry_strategy(),
            scheduler_name=self.scheduler_name,
            security_context=self.pod_security_context,
            service_account_name=self.service_account_name,
            sidecars=self._build_sidecars(),
            synchronization=self.synchronization,
            timeout=self.timeout,
            tolerations=self.tolerations,
            volumes=self._build_volumes(),
        )


__all__ = ["ContainerNode", "ContainerSet"]
