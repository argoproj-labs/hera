from typing import List, Optional, Union

from hera.workflows.env import _BaseEnv
from hera.workflows.env_from import _BaseEnvFrom
from hera.workflows.models import (
    EnvFromSource,
    EnvVar,
    ImagePullPolicy,
    ResourceRequirements,
    UserContainer as _ModelUserContainer,
)
from hera.workflows.resources import Resources
from hera.workflows.volume import _BaseVolume


class UserContainer(_ModelUserContainer):
    env: Optional[List[Union[_BaseEnv, EnvVar]]] = None  # type: ignore[assignment]
    env_from: Optional[List[Union[_BaseEnvFrom, EnvFromSource]]] = None  # type: ignore[assignment]
    image_pull_policy: Optional[Union[str, ImagePullPolicy]] = None  # type: ignore[assignment]
    resources: Optional[Union[Resources, ResourceRequirements]] = None  # type: ignore[assignment]
    volumes: Optional[List[_BaseVolume]] = None

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
            volume_mounts=None if self.volumes is None else [v._build_volume_mount() for v in self.volumes],
            working_dir=self.working_dir,
        )


__all__ = ["UserContainer"]
