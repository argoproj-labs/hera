from typing import Optional

from hera.models import ConfigMapEnvSource as ModelConfigMapEnvSource
from hera.models import EnvFromSource as ModelEnvFromSource
from hera.models import SecretEnvSource as ModelSecretEnvSource


class _BaseEnvFrom:
    prefix: Optional[str] = None

    def build(self) -> ModelEnvFromSource:
        """Constructs and returns the Argo EnvFrom specification"""
        raise NotImplementedError()


class SecretEnvFrom(_BaseEnvFrom, ModelSecretEnvSource):
    def build(self) -> ModelEnvFromSource:
        """Constructs and returns the Argo EnvFrom specification"""
        return ModelEnvFromSource(
            prefix=self.prefix,
            secret_ref=ModelSecretEnvSource(
                name=self.name,
                optional=self.optional,
            ),
        )


class ConfigMapEnvFrom(_BaseEnvFrom, ModelConfigMapEnvSource):
    def build(self) -> ModelEnvFromSource:
        """Constructs and returns the Argo EnvFrom specification"""
        return ModelEnvFromSource(
            prefix=self.prefix,
            config_map_ref=ModelConfigMapEnvSource(
                name=self.name,
                optional=self.optional,
            ),
        )
