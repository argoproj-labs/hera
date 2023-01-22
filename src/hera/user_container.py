from typing import List, Optional

from hera.env import _BaseEnv
from hera.env_from import _BaseEnvFrom
from hera.models import ImagePullPolicy
from hera.models import UserContainer as _ModelUserContainer
from hera.resources import Resources
from hera.volumes import _BaseVolume


class UserContainer(_ModelUserContainer):
    env: Optional[List[_BaseEnv]] = None  # type: ignore[assignment]
    env_from: Optional[List[_BaseEnvFrom]] = None  # type: ignore[assignment]
    image_pull_policy: Optional[ImagePullPolicy] = None  # type: ignore[assignment]
    resources: Optional[Resources] = None  # type: ignore[assignment]
    volumes: Optional[List[_BaseVolume]] = None  # type: ignore[assignment]

    def build(self) -> _ModelUserContainer:
        return _ModelUserContainer(
            args=self.args,
            command=self.command,
            env=None if self.env is None else [e.build() for e in self.env],
            env_from=None if self.env_from is None else [ef.build() for ef in self.env_from],
            image=self.image,
            image_pull_policy=self.image_pull_policy.value if self.image_pull_policy else None,
            lifecycle=self.lifecycle,
            liveness_probe=self.liveness_probe,
            mirror_volume_mounts=self.mirror_volume_mounts,
            name=self.name,
            ports=self.ports,
            readiness_probe=self.readiness_probe,
            resources=None if self.resources is None else self.resources.build(),
            security_context=self.security_context,
            startup_probe=self.startup_probe,
            stdin=self.stdin,
            stdin_once=self.stdin_once,
            termination_message_path=self.termination_message_path,
            termination_message_policy=self.termination_message_policy,
            tty=self.tty,
            volume_devices=self.volume_devices,
            volume_mounts=None if self.volumes is None else [v.to_volume() for v in self.volumes],
            working_dir=self.working_dir,
        )


__all__ = ["UserContainer"]
