from argo_workflows.models import ConfigMapEnvSource, EnvFromSource, SecretEnvSource
from pydantic.main import BaseModel


class BaseEnvFromSpec(BaseModel):
    """Environment variable specification from K8S resources.

    Attributes
    ----------
    prefix: str = ''
        An optional identifier to prepend to each key in the specified resources.
    """

    prefix: str = ''

    @property
    def argo_spec(self) -> EnvFromSource:
        """Constructs and returns the Argo EnvFrom specification"""
        raise NotImplementedError


class SecretEnvFromSpec(BaseEnvFromSpec):
    """Environment variable specification from K8S secrets.

    Attributes
    ----------
    secret_name: str
        The name of the secret to load environments.
    optional: bool = False
        Specify whether the K8S secret must be defined
    """

    secret_name: str
    optional: bool = False

    @property
    def argo_spec(self) -> EnvFromSource:
        """Constructs and returns the Argo EnvFrom specification"""
        return EnvFromSource(
            prefix=self.prefix, secret_ref=SecretEnvSource(name=self.secret_name, optional=self.optional)
        )


class ConfigMapEnvFromSpec(BaseEnvFromSpec):
    """Environment variable specification from K8S config map.

    Attributes
    ----------
    config_map_name: str
        The name of the config map to load environments.
    optional: bool = False
        Specify whether the K8S config map must be defined
    """

    config_map_name: str
    optional: bool = False

    @property
    def argo_spec(self) -> EnvFromSource:
        """Constructs and returns the Argo EnvFrom specification"""
        return EnvFromSource(
            prefix=self.prefix, config_map_ref=ConfigMapEnvSource(name=self.config_map_name, optional=self.optional)
        )
