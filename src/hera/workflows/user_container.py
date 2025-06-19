"""The `hera.workflows.user_container` module provides user container functionality and objects.

UserContainers are used as side containers, so they can run background processes required for the main container.
"""

from typing import List, Optional, Union, cast

from hera.workflows.env import _BaseEnv
from hera.workflows.env_from import _BaseEnvFrom
from hera.workflows.models import (
    EnvFromSource,
    EnvVar,
    ImagePullPolicy,
    ResourceRequirements,
    UserContainer as _ModelUserContainer,
    VolumeMount as _ModelVolumeMount,
)
from hera.workflows.resources import Resources
from hera.workflows.volume import _BaseVolume


class UserContainer(_ModelUserContainer):
    """`UserContainer` is a container type that is specifically used as a side container."""

    # TODO: Use EnvMixin (currently a circular import)
    env: Optional[List[Union[_BaseEnv, EnvVar]]] = None  # type: ignore[assignment]
    env_from: Optional[List[Union[_BaseEnvFrom, EnvFromSource]]] = None  # type: ignore[assignment]
    image_pull_policy: Optional[Union[str, ImagePullPolicy]] = None  # type: ignore[assignment]
    resources: Optional[Union[Resources, ResourceRequirements]] = None  # type: ignore[assignment]
    volumes: Optional[List[_BaseVolume]] = None

    def _build_image_pull_policy(self) -> Optional[str]:
        """Processes the image pull policy field and optionally returns a string value from `ImagePullPolicy` enum."""
        if self.image_pull_policy is None:
            return None
        elif isinstance(self.image_pull_policy, ImagePullPolicy):
            return self.image_pull_policy.value

        # this helps map image pull policy values as a convenience
        policy_mapper = {
            # the following 2 are "normal" entries
            **{ipp.name: ipp for ipp in ImagePullPolicy},
            **{ipp.value: ipp for ipp in ImagePullPolicy},
            # some users might submit the policy in lowercase & without underscores
            **{ipp.value.lower(): ipp for ipp in ImagePullPolicy},
        }
        try:
            return ImagePullPolicy[policy_mapper[self.image_pull_policy].name].value
        except KeyError as e:
            raise KeyError(
                f"Supplied image policy {self.image_pull_policy} is not valid. "
                "Use one of {ImagePullPolicy.__members__}"
            ) from e

    def _build_volume_mounts(self) -> Optional[List[_ModelVolumeMount]]:
        """Processes the volume mounts field and returns a generated `VolumeMount`."""
        volume_mounts = self.volume_mounts
        # extra volume mounts stem from using custom Hera volumes, which dynamically provision PVs + PVCs
        extra_volume_mounts = None if self.volumes is None else [v._build_volume_mount() for v in self.volumes]
        if volume_mounts is None:
            volume_mounts = extra_volume_mounts
        elif extra_volume_mounts is not None:
            volume_mounts.extend(extra_volume_mounts)

        return volume_mounts

    def build(self) -> _ModelUserContainer:
        """Builds the Hera auto-generated model of the user container."""
        env: List[EnvVar] = [
            var if isinstance(var, EnvVar) else cast(_BaseEnv, var).build() for var in (self.env or [])
        ]
        env_from: List[EnvFromSource] = [
            var if isinstance(var, EnvFromSource) else cast(_BaseEnvFrom, var).build() for var in (self.env_from or [])
        ]

        return _ModelUserContainer(
            args=self.args,
            command=self.command,
            env=env or None,
            env_from=env_from or None,
            image=self.image,
            image_pull_policy=self._build_image_pull_policy(),
            lifecycle=self.lifecycle,
            liveness_probe=self.liveness_probe,
            mirror_volume_mounts=self.mirror_volume_mounts,
            name=self.name,
            ports=self.ports,
            readiness_probe=self.readiness_probe,
            resources=self.resources
            if isinstance(self.resources, ResourceRequirements)
            else self.resources.build()
            if self.resources
            else None,
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


__all__ = ["UserContainer"]
