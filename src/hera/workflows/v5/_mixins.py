from typing import Dict, List, Optional, Union, cast

from pydantic import validator

from hera.workflows._base_model import BaseModel as _BaseModel
from hera.workflows.models import (
    HTTP,
    Affinity,
    Artifact,
    ArtifactLocation,
    ContainerPort,
    EnvFromSource,
    EnvVar,
    ExecutorConfig,
    HostAlias,
    ImagePullPolicy,
)
from hera.workflows.models import Inputs as ModelInputs
from hera.workflows.models import IntOrString, Memoize, Metadata, Metrics
from hera.workflows.models import Outputs as ModelOutputs
from hera.workflows.models import Parameter as ModelParameter
from hera.workflows.models import (
    Plugin,
    PodSecurityContext,
    Probe,
    ResourceRequirements,
    RetryStrategy,
    Synchronization,
    TerminationMessagePolicy,
    Toleration,
)
from hera.workflows.models import UserContainer as ModelUserContainer
from hera.workflows.models import VolumeDevice, VolumeMount
from hera.workflows.v5.env import _BaseEnv
from hera.workflows.v5.env_from import _BaseEnvFrom
from hera.workflows.v5.parameter import Parameter
from hera.workflows.v5.resources import Resources
from hera.workflows.v5.user_container import UserContainer
from hera.workflows.v5.volume import _BaseVolume

Inputs = List[Union[Artifact, Parameter, ModelParameter]]
Outputs = List[Union[Artifact, Parameter, ModelParameter]]


class _BaseMixin(_BaseModel):
    pass


class _ContainerMixin(_BaseMixin):
    image: str
    image_pull_policy: Optional[Union[str, ImagePullPolicy]] = None

    @validator('image_pull_policy', pre=True)
    def _convert_image_pull_policy(cls, v):
        if v is None or isinstance(v, ImagePullPolicy):
            return v
        v = cast(str, v)
        return ImagePullPolicy[v.lower()]  # must be str


class _IOMixin(_BaseMixin):
    inputs: Optional[Union[Inputs, ModelInputs]] = None
    outputs: Optional[Union[Outputs, ModelOutputs]] = None

    @validator("inputs", pre=True)
    def _convert_inputs(cls, v):
        if v is None:
            return None

        result = ModelInputs()
        if isinstance(v, list):
            for value in v:
                if isinstance(value, Artifact):
                    result.artifacts = [value] if result.artifacts is None else result.artifacts + [value]
                elif isinstance(value, Parameter):
                    result.parameters = (
                        [value.as_input()] if result.parameters is None else result.parameters + [value.as_input()]
                    )
                elif isinstance(value, ModelParameter):
                    result.parameters = [value] if result.parameters is None else result.parameters + [value]
                else:
                    raise ValueError(
                        f"Unrecognized `inputs` type {type(v)}. Accepted types are "
                        "`hera.workflows.models.Artifact`, `hera.workflows.Parameter`, "
                        "`hera.workflows.models.Parameter`, and `hera.workflows.models.Inputs`"
                    )
        return v  # must be ModelInputs

    @validator("outputs", pre=True)
    def _convert_outputs(cls, v):
        if v is None:
            return None

        result = ModelOutputs()
        if isinstance(v, list):
            for value in v:
                if isinstance(value, Artifact):
                    result.artifacts = [value] if result.artifacts is None else result.artifacts + [value]
                elif isinstance(value, Parameter):
                    result.parameters = (
                        [value.as_output()] if result.parameters is None else result.parameters + [value.as_output()]
                    )
                elif isinstance(value, ModelParameter):
                    result.parameters = [value] if result.parameters is None else result.parameters + [value]
                else:
                    raise ValueError(
                        f"Unrecognized `outputs` type {type(v)}. Accepted types are "
                        "`hera.workflows.models.Artifact`, `hera.workflows.Parameter`, "
                        "`hera.workflows.models.Parameter`, and `hera.workflows.models.Outputs`"
                    )
        return v  # must be ModelOutputs


class _EnvMixin(_BaseMixin):
    env: Optional[List[Union[_BaseEnv, EnvVar]]] = None
    env_from: Optional[List[Union[_BaseEnvFrom, EnvFromSource]]] = None

    @validator('env', pre=True)
    def _convert_env(cls, v):
        if v is None or isinstance(v, EnvVar):
            return v

        v = cast(_BaseEnv, v)
        return v.build()

    @validator('env_from', pre=True)
    def _convert_env_from(cls, v):
        if v is None or isinstance(v, EnvFromSource):
            return v

        v = cast(_BaseEnvFrom, v)
        return v.build()


class _TemplateMixin(_BaseMixin):
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
    metadata: Optional[Metadata] = None
    metrics: Optional[Metrics] = None
    node_selector: Optional[Dict[str, str]] = None
    http: Optional[HTTP] = None
    plugin: Optional[Plugin] = None
    pod_spec_patch: Optional[str] = None
    priority: Optional[int] = None
    priority_class_name: Optional[str] = None
    retry_strategy: Optional[RetryStrategy] = None
    scheduler_name: Optional[str] = None
    liveness_probe: Optional[Probe] = None
    ports: Optional[List[ContainerPort]] = None
    readiness_probe: Optional[Probe] = None
    template_security_context: Optional[PodSecurityContext] = None
    startup_probe: Optional[Probe] = None
    stdin: Optional[bool] = None
    stdin_once: Optional[bool] = None
    termination_message_path: Optional[str] = None
    termination_message_policy: Optional[TerminationMessagePolicy] = None
    tty: Optional[bool] = None
    service_account_name: Optional[str] = None
    sidecars: Optional[List[UserContainer]] = None
    synchronization: Optional[Synchronization] = None
    timeout: Optional[str] = None
    tolerations: Optional[List[Toleration]] = None


class _ResourceMixin(_BaseMixin):
    resources: Optional[Union[ResourceRequirements, Resources]] = None

    @validator('resources', pre=True)
    def _convert_resources(cls, v):
        if v is None or isinstance(v, ResourceRequirements):
            return v

        v = cast(Resources, v)
        return v.build()


class _VolumeMountMixin(_BaseMixin):
    volume_devices: Optional[List[VolumeDevice]] = None
    volume_mounts: Optional[List[VolumeMount]] = None
    volumes: Optional[List[_BaseVolume]] = None

    @validator('volume_mounts', pre=True)
    def _convert_volumes(cls, v, values):
        volumes: Optional[List[_BaseVolume]] = values.get('volumes')
        if v is None and volumes is None:
            return None

        result = None if volumes is None else [vol.to_mount() for vol in volumes]
        if v is None:
            return result
        return v + result
