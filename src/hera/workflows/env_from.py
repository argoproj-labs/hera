"""The `hera.workflows.env_from` module provides implementations of environment variable classes that can be created from K8s objects.

`EnvFrom` classes differs from [Env](env.md) classes as `EnvFrom` uses a source to retrieve a variable from,
and you can only prefix the name with something. The `Env` classes can create new independent variables.
"""

from dataclasses import dataclass
from typing import Optional

from hera.workflows.models import (
    ConfigMapEnvSource as _ModelConfigMapEnvSource,
    EnvFromSource as _ModelEnvFromSource,
    SecretEnvSource as _ModelSecretEnvSource,
)


@dataclass(kw_only=True)
class _BaseEnvFrom:
    prefix: Optional[str] = None

    def build(self) -> _ModelEnvFromSource:
        """Constructs and returns the Argo EnvFrom specification."""
        raise NotImplementedError()


@dataclass(kw_only=True)
class SecretEnvFrom(_BaseEnvFrom):
    """Exposes a K8s secret as an environment variable."""

    name: Optional[str] = None
    optional: Optional[bool] = None

    def build(self) -> _ModelEnvFromSource:
        """Constructs and returns the Argo EnvFrom specification."""
        return _ModelEnvFromSource(
            prefix=self.prefix,
            secret_ref=_ModelSecretEnvSource(
                name=self.name,
                optional=self.optional,
            ),
        )


@dataclass(kw_only=True)
class ConfigMapEnvFrom(_BaseEnvFrom):
    """Exposes a K8s config map's value as an environment variable."""

    name: Optional[str] = None
    optional: Optional[bool] = None

    def build(self) -> _ModelEnvFromSource:
        """Constructs and returns the Argo EnvFrom specification."""
        return _ModelEnvFromSource(
            prefix=self.prefix,
            config_map_ref=_ModelConfigMapEnvSource(
                name=self.name,
                optional=self.optional,
            ),
        )


__all__ = [*[c.__name__ for c in _BaseEnvFrom.__subclasses__()]]
