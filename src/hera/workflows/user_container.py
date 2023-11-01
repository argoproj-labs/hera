"""The user container module provides user container functionality and objects."""
from typing import Any, Dict, List, Optional, Union

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

# TODO: Mixins imports user container, so this avoids a circular import. Fix in a future release
EnvT = Optional[
    Union[
        _BaseEnv,
        EnvVar,
        List[Union[_BaseEnv, EnvVar, Dict[str, Any]]],
        Dict[str, Any],
    ]
]
"""`EnvT` is the core Hera type for environment variables.

The env type enables setting single valued environment variables, lists of environment variables, or dictionary 
mappings of env variables names to values, which are automatically parsed by Hera.
"""

# TODO: Mixins imports user container, so this avoids a circular import. Fix in a future release
EnvFromT = Optional[Union[_BaseEnvFrom, EnvFromSource, List[Union[_BaseEnvFrom, EnvFromSource]]]]
"""`EnvFromT` is the core Hera type for environment variables derived from Argo/Kubernetes sources.

This env type enables specifying environment variables in base form, as `hera.workflows.env` form, or lists of the 
aforementioned objects.
"""


class UserContainer(_ModelUserContainer):
    """`UserContainer` is a container type that is specifically used as a side container."""

    env: EnvT = None
    env_from: EnvFromT = None  # type: ignore[assignment]
    image_pull_policy: Optional[Union[str, ImagePullPolicy]] = None  # type: ignore[assignment]
    resources: Optional[Union[Resources, ResourceRequirements]] = None  # type: ignore[assignment]
    volumes: Optional[List[_BaseVolume]] = None

    def _build_resources(self) -> Optional[ResourceRequirements]:
        """Parses the resources and returns a generated `ResourceRequirements` object."""
        if self.resources is None or isinstance(self.resources, ResourceRequirements):
            return self.resources
        return self.resources.build()

    def _build_env(self) -> Optional[List[EnvVar]]:
        """Processes the `env` field and returns a list of generated `EnvVar` or `None`."""
        if self.env is None:
            return None

        result: List[EnvVar] = []
        env = self.env if isinstance(self.env, list) else [self.env]
        for e in env:
            if isinstance(e, EnvVar):
                result.append(e)
            elif issubclass(e.__class__, _BaseEnv):
                result.append(e.build())
            elif isinstance(e, dict):
                for k, v in e.items():
                    result.append(EnvVar(name=k, value=v))

        # returning `None` for `envs` means the submission to the server will not even have the `envs` field
        # set, which saves some space
        return result if result else None

    def _build_env_from(self) -> Optional[List[EnvFromSource]]:
        """Processes the `env_from` field and returns a list of generated `EnvFrom` or `None`."""
        if self.env_from is None:
            return None

        result: List[EnvFromSource] = []
        env_from = self.env_from if isinstance(self.env_from, list) else [self.env_from]
        for e in env_from:
            if isinstance(e, EnvFromSource):
                result.append(e)
            elif issubclass(e.__class__, _BaseEnvFrom):
                result.append(e.build())

        # returning `None` for `envs` means the submission to the server will not even have the `env_from` field
        # set, which saves some space
        return result if result else None

    def _build_image_pull_policy(self) -> Optional[str]:
        """Processes the image pull policy field and returns a generated `ImagePullPolicy` enum."""
        if self.image_pull_policy is None:
            return None
        elif isinstance(self.image_pull_policy, ImagePullPolicy):
            return self.image_pull_policy.value

        # this helps map image pull policy values as a convenience
        policy_mapper = {
            # the following 2 are "normal" entries
            **{ipp.name: ipp for ipp in ImagePullPolicy},
            **{ipp.value: ipp for ipp in ImagePullPolicy},
            # some users might submit the policy without underscores
            **{ipp.value.lower().replace("_", ""): ipp for ipp in ImagePullPolicy},
            # some users might submit the policy in lowercase
            **{ipp.name.lower(): ipp for ipp in ImagePullPolicy},
        }
        try:
            return ImagePullPolicy[policy_mapper[self.image_pull_policy].name].value
        except KeyError as e:
            raise KeyError(
                f"Supplied image policy {self.image_pull_policy} is not valid. "
                "Use one of {ImagePullPolicy.__members__}"
            ) from e

    def build(self) -> _ModelUserContainer:
        """Builds the Hera auto-generated model of the user container."""
        return _ModelUserContainer(
            args=self.args,
            command=self.command,
            env=self._build_env(),
            env_from=self._build_env_from(),
            image=self.image,
            image_pull_policy=self._build_image_pull_policy(),
            lifecycle=self.lifecycle,
            liveness_probe=self.liveness_probe,
            mirror_volume_mounts=self.mirror_volume_mounts,
            name=self.name,
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
            volume_mounts=None if self.volumes is None else [v._build_volume_mount() for v in self.volumes],
            working_dir=self.working_dir,
        )


__all__ = ["UserContainer"]
