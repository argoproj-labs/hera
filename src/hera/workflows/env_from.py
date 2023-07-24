"""A module that provides implementations of environment variables that can be created from K8s objects."""
from typing import Optional

from hera.shared._base_model import BaseModel as _BaseModel
from hera.workflows.models import (
    ConfigMapEnvSource as _ModelConfigMapEnvSource,
    EnvFromSource as _ModelEnvFromSource,
    SecretEnvSource as _ModelSecretEnvSource,
)


class _BaseEnvFrom(_BaseModel):
    prefix: Optional[str] = None

    def build(self) -> _ModelEnvFromSource:
        """Constructs and returns the Argo EnvFrom specification."""
        raise NotImplementedError()


class SecretEnvFrom(_BaseEnvFrom, _ModelSecretEnvSource):
    """Exposes a K8s secret as an environment variable."""

    def build(self) -> _ModelEnvFromSource:
        """Constructs and returns the Argo EnvFrom specification."""
        return _ModelEnvFromSource(
            prefix=self.prefix,
            secret_ref=_ModelSecretEnvSource(
                name=self.name,
                optional=self.optional,
            ),
        )


class ConfigMapEnvFrom(_BaseEnvFrom, _ModelConfigMapEnvSource):
    """Exposes a K8s config map's value as an environment variable."""

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
