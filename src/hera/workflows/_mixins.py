from __future__ import annotations

from typing import Any, Dict, List, Optional, TypeVar, Union, cast

from hera.shared.global_config import GlobalConfig
from hera.workflows._base_model import BaseMixin
from hera.workflows._context import SubNodeMixin, _context
from hera.workflows.artifact import Artifact
from hera.workflows.env import _BaseEnv
from hera.workflows.env_from import _BaseEnvFrom
from hera.workflows.models import (
    HTTP,
    Affinity,
    Artifact as ModelArtifact,
    ArtifactLocation,
    ContainerPort,
    EnvFromSource,
    EnvVar,
    ExecutorConfig,
    HostAlias,
    ImagePullPolicy,
    Inputs as ModelInputs,
    IntOrString,
    Memoize,
    Metadata,
    Metrics,
    Outputs as ModelOutputs,
    Parameter as ModelParameter,
    Plugin,
    PodSecurityContext,
    Probe,
    ResourceRequirements,
    RetryStrategy,
    Synchronization,
    TerminationMessagePolicy,
    Toleration,
    UserContainer as ModelUserContainer,
    Volume,
    VolumeDevice,
    VolumeMount,
)
from hera.workflows.parameter import Parameter
from hera.workflows.resources import Resources
from hera.workflows.user_container import UserContainer
from hera.workflows.volume import _BaseVolume

Inputs = Union[ModelInputs, List[Union[Parameter, ModelParameter, Artifact, ModelArtifact]]]
Outputs = Union[ModelOutputs, List[Union[Parameter, ModelParameter, Artifact, ModelArtifact]]]
Env = Optional[List[Union[_BaseEnv, EnvVar]]]
EnvFrom = Optional[List[Union[_BaseEnvFrom, EnvFromSource]]]
TContext = TypeVar("TContext", bound="ContextMixin")


class ContextMixin(BaseMixin):
    def __enter__(self: TContext) -> TContext:
        """Enter the context of the workflow"""

        _context.enter(self)
        return self

    def __exit__(self, *_) -> None:
        """Leave the context of the workflow.

        This supports using `with Workflow(...)`.
        """
        _context.exit()

    def _add_sub(self, node: Any) -> Any:
        raise NotImplementedError()


class ContainerMixin(BaseMixin):
    image: str = GlobalConfig.image
    image_pull_policy: Optional[Union[str, ImagePullPolicy]] = None

    liveness_probe: Optional[Probe] = None
    ports: Optional[List[ContainerPort]] = None
    readiness_probe: Optional[Probe] = None
    startup_probe: Optional[Probe] = None
    stdin: Optional[bool] = None
    stdin_once: Optional[bool] = None
    termination_message_path: Optional[str] = None
    termination_message_policy: Optional[TerminationMessagePolicy] = None
    tty: Optional[bool] = None

    def _build_image_pull_policy(self) -> Optional[ImagePullPolicy]:
        if self.image_pull_policy is None or isinstance(self.image_pull_policy, ImagePullPolicy):
            return self.image_pull_policy
        return ImagePullPolicy[self.image_pull_policy.lower()]


class IOMixin(BaseMixin):
    inputs: Inputs = []
    outputs: Outputs = []

    def _build_inputs(self) -> Optional[ModelInputs]:
        if not self.inputs:
            return None
        elif isinstance(self.inputs, ModelInputs):
            return self.inputs

        result = ModelInputs()
        for value in self.inputs:
            if isinstance(value, Parameter):
                result.parameters = (
                    [value.as_input()] if result.parameters is None else result.parameters + [value.as_input()]
                )
            elif isinstance(value, ModelParameter):
                result.parameters = [value] if result.parameters is None else result.parameters + [value]
            elif isinstance(value, Artifact):
                result.artifacts = (
                    [value._build_artifact()]
                    if result.artifacts is None
                    else result.artifacts + [value._build_artifact()]
                )
            else:
                result.artifacts = [value] if result.artifacts is None else result.artifacts + [value]

        if result.parameters is None and result.artifacts is None:
            return None
        return result

    def _build_outputs(self) -> Optional[ModelOutputs]:
        if not self.outputs:
            return None
        elif isinstance(self.outputs, ModelOutputs):
            return self.outputs

        result = ModelOutputs()
        for value in self.outputs:
            if isinstance(value, Parameter):
                result.parameters = (
                    [value.as_output()] if result.parameters is None else result.parameters + [value.as_output()]
                )
            elif isinstance(value, ModelParameter):
                result.parameters = [value] if result.parameters is None else result.parameters + [value]
            elif isinstance(value, Artifact):
                result.artifacts = (
                    [value._build_artifact()]
                    if result.artifacts is None
                    else result.artifacts + [value._build_artifact()]
                )
            else:
                result.artifacts = [value] if result.artifacts is None else result.artifacts + [value]

        if result.parameters is None and result.artifacts is None:
            return None
        return result


class EnvMixin(BaseMixin):
    env: Env = None
    env_from: EnvFrom = None

    def _build_env(self) -> Optional[EnvVar]:
        if self.env is None or isinstance(self.env, EnvVar):
            return self.env

        v = cast(_BaseEnv, self.env)
        return v.build()

    def _build_env_from(self) -> Optional[EnvFromSource]:
        if self.env_from is None or isinstance(self.env_from, EnvFromSource):
            return self.env_from

        v = cast(_BaseEnvFrom, self.env_from)
        return v.build()


class TemplateMixin(SubNodeMixin):
    active_deadline_seconds: Optional[Union[int, str, IntOrString]] = None
    affinity: Optional[Affinity] = None
    archive_location: Optional[ArtifactLocation] = None
    automount_service_account_token: Optional[bool] = None
    daemon: Optional[bool] = None
    executor: Optional[ExecutorConfig] = None
    fail_fast: Optional[bool] = None
    host_aliases: Optional[List[HostAlias]] = None
    init_containers: Optional[List[Union[UserContainer, ModelUserContainer]]] = None
    memoize: Optional[Memoize] = None
    annotations: Optional[Dict[str, str]] = None
    labels: Optional[Dict[str, str]] = None
    metrics: Optional[Metrics] = None
    name: Optional[str] = None
    node_selector: Optional[Dict[str, str]] = None
    parallelism: Optional[int] = None
    http: Optional[HTTP] = None
    plugin: Optional[Plugin] = None
    pod_spec_patch: Optional[str] = None
    priority: Optional[int] = None
    priority_class_name: Optional[str] = None
    retry_strategy: Optional[RetryStrategy] = None
    scheduler_name: Optional[str] = None
    pod_security_context: Optional[PodSecurityContext] = None
    service_account_name: Optional[str] = None
    sidecars: Optional[List[UserContainer]] = None
    synchronization: Optional[Synchronization] = None
    timeout: Optional[str] = None
    tolerations: Optional[List[Toleration]] = None

    def _build_active_deadline_seconds(self) -> Optional[IntOrString]:
        if self.active_deadline_seconds is None:
            return None

        return IntOrString(__root__=str(self.active_deadline_seconds))

    def _build_metadata(self) -> Optional[Metadata]:
        if self.annotations is None and self.labels is None:
            return None

        return Metadata(
            annotations=self.annotations,
            labels=self.labels,
        )


class ResourceMixin(BaseMixin):
    resources: Optional[Union[ResourceRequirements, Resources]] = None

    def _build_resources(self) -> Optional[ResourceRequirements]:
        if self.resources is None or isinstance(self.resources, ResourceRequirements):
            return self.resources

        return self.resources.build()


class VolumeMountMixin(BaseMixin):
    volume_devices: Optional[List[VolumeDevice]] = None
    volume_mounts: Optional[List[VolumeMount]] = None
    volumes: Optional[List[_BaseVolume]] = None

    def _build_volume_mounts(self) -> Optional[List[VolumeMount]]:
        if self.volume_mounts is None and self.volumes is None:
            return None

        result = None if self.volumes is None else [v._build_volume_mount() for v in self.volumes]

        if result is None and self.volume_mounts is None:
            return None
        elif result is None and self.volume_mounts is not None:
            return self.volume_mounts
        return cast(List[VolumeMount], self.volume_mounts) + cast(List[VolumeMount], result)

    def _build_volumes(self) -> Optional[List[Volume]]:
        if self.volumes is None:
            return None
        return [v._build_volume() for v in self.volumes]
