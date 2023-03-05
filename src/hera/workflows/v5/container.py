from __future__ import annotations

from typing import List, Optional

from hera.workflows.models import (
    Arguments,
    Artifact,
    Container as _ModelContainer,
    Lifecycle,
    SecurityContext,
    Template as _ModelTemplate,
)
from hera.workflows.v5._mixins import (
    _ContainerMixin,
    _EnvMixin,
    _IOMixin,
    _ResourceMixin,
    _SubNodeMixin,
    _TemplateMixin,
    _VolumeMountMixin,
)
from hera.workflows.v5.parameter import Parameter


class Container(
    _IOMixin,
    _ContainerMixin,
    _EnvMixin,
    _TemplateMixin,
    _ResourceMixin,
    _SubNodeMixin,
    _VolumeMountMixin,
):
    args: Optional[List[str]] = None
    command: Optional[List[str]] = None
    lifecycle: Optional[Lifecycle] = None
    security_context: Optional[SecurityContext] = None
    working_dir: Optional[str] = None

    def _build_container(self) -> _ModelContainer:
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
        return _ModelTemplate(
            active_deadline_seconds=self.active_deadline_seconds,
            affinity=self.affinity,
            archive_location=self.archive_location,
            automount_service_account_token=self.automount_service_account_token,
            container=self._build_container(),
            container_set=None,
            daemon=self.daemon,
            dag=None,
            data=None,
            executor=self.executor,
            fail_fast=self.fail_fast,
            host_aliases=self.host_aliases,
            http=None,
            init_containers=self.init_containers,
            inputs=self._build_inputs(),
            memoize=self.memoize,
            metadata=self._build_metadata(),
            metrics=self.metrics,
            name=self.name,
            node_selector=self.node_selector,
            outputs=self._build_outputs(),
            parallelism=None,
            plugin=self.plugin,
            pod_spec_patch=self.pod_spec_patch,
            priority=self.priority,
            priority_class_name=self.priority_class_name,
            resource=self._build_resources(),
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
            volumes=self._build_volumes(),
        )

    def _build_arguments(self) -> Optional[Arguments]:
        # parameters = [obj.as_argument() for obj in self.inputs if isinstance(obj, Parameter)]
        # parameters = [p for p in parameters if p is not None]  # Some parameters might not resolve
        if self.inputs is None:
            return None

        parameters = [p for p in self.inputs if isinstance(p, Parameter)]
        artifacts = [a for a in self.inputs if isinstance(a, Artifact)]
        if len(parameters) == 0 and len(artifacts) == 0:
            return None
        return Arguments(
            artifacts=None if len(artifacts) == 0 else artifacts,
            parameters=None if len(parameters) == 0 else parameters,
        )
