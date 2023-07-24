"""The container module provides the Container class.

See https://argoproj.github.io/argo-workflows/workflow-concepts/#container
for more on containers.
"""
from __future__ import annotations

from typing import List, Optional

from hera.workflows._mixins import (
    CallableTemplateMixin,
    ContainerMixin,
    EnvIOMixin,
    ResourceMixin,
    TemplateMixin,
    VolumeMountMixin,
)
from hera.workflows.models import (
    Container as _ModelContainer,
    Lifecycle,
    SecurityContext,
    Template as _ModelTemplate,
)


class Container(
    EnvIOMixin,
    ContainerMixin,
    TemplateMixin,
    ResourceMixin,
    VolumeMountMixin,
    CallableTemplateMixin,
):
    """The Container template type defines a container to run on Argo.

    The container generally consists of running a Docker container remotely, which is configured via fields such as
    `command` (the command to run to start the container), `args` (arguments for the container), `working_dir` (for
    setting the active working directory relative to container execution), etc.
    """

    args: Optional[List[str]] = None
    command: Optional[List[str]] = None
    lifecycle: Optional[Lifecycle] = None
    security_context: Optional[SecurityContext] = None
    working_dir: Optional[str] = None

    def _build_container(self) -> _ModelContainer:
        """Builds the generated `Container` representation."""
        return _ModelContainer(
            args=self.args,
            command=self.command,
            env=self._build_env(),
            env_from=self._build_env_from(),
            image=self.image,
            image_pull_policy=self._build_image_pull_policy(),
            lifecycle=self.lifecycle,
            liveness_probe=self.liveness_probe,
            ports=self.ports,
            readiness_probe=self.readiness_probe,
            resources=self._build_resources(),
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

    def _build_template(self) -> _ModelTemplate:
        """Builds the generated `Template` representation of the container."""
        return _ModelTemplate(
            active_deadline_seconds=self.active_deadline_seconds,
            affinity=self.affinity,
            archive_location=self.archive_location,
            automount_service_account_token=self.automount_service_account_token,
            container=self._build_container(),
            daemon=self.daemon,
            executor=self.executor,
            fail_fast=self.fail_fast,
            host_aliases=self.host_aliases,
            init_containers=self.init_containers,
            inputs=self._build_inputs(),
            memoize=self.memoize,
            metadata=self._build_metadata(),
            metrics=self._build_metrics(),
            name=self.name,
            node_selector=self.node_selector,
            outputs=self._build_outputs(),
            plugin=self.plugin,
            pod_spec_patch=self.pod_spec_patch,
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
            volumes=self._build_volumes(),
        )


__all__ = ["Container"]
