from typing import Optional

from hera.models import ConfigMapEnvSource as _ModelConfigMapEnvSource
from hera.models import EnvFromSource as _ModelEnvFromSource
from hera.models import SecretEnvSource as _ModelSecretEnvSource


class _BaseEnvFrom:
    prefix: Optional[str] = None

    def build(self) -> _ModelEnvFromSource:
        """Constructs and returns the Argo EnvFrom specification"""
        raise NotImplementedError()


class SecretEnvFrom(_BaseEnvFrom, _ModelSecretEnvSource):
    def build(self) -> _ModelEnvFromSource:
        """Constructs and returns the Argo EnvFrom specification"""
        return _ModelEnvFromSource(
            prefix=self.prefix,
            secret_ref=_ModelSecretEnvSource(
                name=self.name,
                optional=self.optional,
            ),
        )


class ConfigMapEnvFrom(_BaseEnvFrom, _ModelConfigMapEnvSource):
    def build(self) -> _ModelEnvFromSource:
        """Constructs and returns the Argo EnvFrom specification"""
        return _ModelEnvFromSource(
            prefix=self.prefix,
            config_map_ref=_ModelConfigMapEnvSource(
                name=self.name,
                optional=self.optional,
            ),
        )


__all__ = [*[c.__name__ for c in _BaseEnvFrom.__subclasses__()]]
