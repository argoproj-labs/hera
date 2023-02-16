from typing import List, Optional, Union

from pydantic import validator

from hera.workflows.models import (
    EnvFromSource,
    EnvVar,
    ImagePullPolicy,
    ResourceRequirements,
)
from hera.workflows.models import UserContainer as _ModelUserContainer
from hera.workflows.v5.buildable import Buildable
from hera.workflows.v5.env import _BaseEnv
from hera.workflows.v5.env_from import _BaseEnvFrom
from hera.workflows.v5.resources import Resources
from hera.workflows.v5.volume import _BaseVolume


class UserContainer(Buildable, _ModelUserContainer):
    env: Optional[List[Union[_BaseEnv, EnvVar]]] = None  # type: ignore[assignment]
    env_from: Optional[List[Union[_BaseEnvFrom, EnvFromSource]]] = None  # type: ignore[assignment]
    image_pull_policy: Optional[Union[str, ImagePullPolicy]] = None  # type: ignore[assignment]
    resources: Optional[Union[Resources, ResourceRequirements]] = None  # type: ignore[assignment]
    volumes: Optional[List[_BaseVolume]] = None

    @validator('env', pre=True)
    def _convert_env(cls, v):
        if v is None:
            return None

        result = []
        for e in v:
            if isinstance(v, _BaseEnv):
                result.append(e.build())
            elif isinstance(v, EnvVar):
                result.append(e)
            else:
                raise ValueError(
                    f"Unrecognized `env` type {type(e)}. Accepted types are `hera.workflows.models.EnvVar` and "
                    "`hera.workflows.env._BaseEnv`"
                )
        return result

    @validator('env_from', pre=True)
    def _convert_env_from(cls, v):
        if v is None:
            return None

        result = []
        for e in v:
            if isinstance(v, _BaseEnvFrom):
                result.append(e.build())
            elif isinstance(v, EnvFromSource):
                result.append(e)
            else:
                raise ValueError(
                    f"Unrecognized `env_from` type {type(e)}. Accepted types are `hera.workflows.models.EnvFromSource` "
                    "and `hera.workflows.env_from._BaseEnvFrom`"
                )
        return result

    @validator('image_pull_policy', pre=True)
    def _convert_image_pull_policy(cls, v):
        if v is None:
            return None

        if isinstance(v, ImagePullPolicy):
            return v.value
        elif isinstance(v, str):
            return v

        raise ValueError(
            f"Unrecognized `image_pull_policy` type {type(v)}. Accepted types are "
            "`hera.workflows.models.ImagePullPolicy` or `str`"
        )

    @validator('resources', pre=True)
    def _convert_resources(cls, v):
        if v is None:
            return None

        if isinstance(v, ResourceRequirements):
            return v
        elif isinstance(v, Resources):
            return v.build()

        raise ValueError(
            f"Unrecognized `resources` type {type(v)}. Accepted types are "
            "`hera.workflows.models.ResourceRequirements` or `hera.workflows.resources.Resources`"
        )

    @validator('volume_mounts', pre=True)
    def _convert_volumes(cls, v, values):
        volumes: Optional[List[_BaseVolume]] = values.get('volumes')
        if v is None and volumes is None:
            return None

        result = None if volumes is None else [vol.to_mount() for vol in volumes]
        if v is None:
            return result
        return v + result

    def build(self) -> _ModelUserContainer:
        return _ModelUserContainer(
            args=self.args,
            command=self.command,
            env=self.env,
            env_from=self.env_from,
            image=self.image,
            image_pull_policy=self.image_pull_policy,
            lifecycle=self.lifecycle,
            liveness_probe=self.liveness_probe,
            mirror_volume_mounts=self.mirror_volume_mounts,
            name=self.name,
            ports=self.ports,
            readiness_probe=self.readiness_probe,
            resources=self.resources,
            security_context=self.security_context,
            startup_probe=self.startup_probe,
            stdin=self.stdin,
            stdin_once=self.stdin_once,
            termination_message_path=self.termination_message_path,
            termination_message_policy=self.termination_message_policy,
            tty=self.tty,
            volume_devices=self.volume_devices,
            volume_mounts=None if self.volumes is None else [v.to_mount() for v in self.volumes],
            working_dir=self.working_dir,
        )


__all__ = ["UserContainer", "EnvVar", "EnvFromSource", "ImagePullPolicy", "Resources", "ResourceRequirements"]
