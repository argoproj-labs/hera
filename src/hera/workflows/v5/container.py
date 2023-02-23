from typing import List, Optional

from hera.workflows.models import Arguments, Artifact
from hera.workflows.models import Container as _ModelContainer
from hera.workflows.models import DAGTask, Lifecycle, SecurityContext
from hera.workflows.models import Template as _ModelTemplate
from hera.workflows.v5._mixins import (
    _ContainerMixin,
    _DAGTaskMixin,
    _EnvMixin,
    _IOMixin,
    _ResourceMixin,
    _TemplateMixin,
    _VolumeMountMixin,
)
from hera.workflows.v5.buildable import Buildable
from hera.workflows.v5.parameter import Parameter


class Container(
    Buildable, _IOMixin, _DAGTaskMixin, _ContainerMixin, _EnvMixin, _TemplateMixin, _ResourceMixin, _VolumeMountMixin
):
    name: str
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
            name=self.name,
            ports=self.ports,
            readiness_probe=self.readiness_probe,
            resources=self._build_resources(),
            security_context=self.security_context,
            startup_probe=self.startup_probe,
            stdin=self.stdin,
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
        return Arguments(artifacts=artifacts, parameters=parameters)

    def _build_dag_task(self) -> DAGTask:
        return DAGTask(
            name=self.name,
            arguments=self._build_arguments(),
            continue_on=self.continue_on,
            dependencies=self.dependencies,
            depends=self.depends,
            hooks=self.hooks,
            inline=self.inline,
            on_exit=self.on_exit,
            template=self.name,
            when=self.when,
            with_items=self.with_items,
            with_param=self.with_param,
            with_sequence=self.with_sequence,
        )
