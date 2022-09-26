from dataclasses import dataclass

from argo_workflows.models import ConfigMapEnvSource, EnvFromSource, SecretEnvSource

# TODO Generalize from classes in volumes.py


@dataclass
class _NamedConfigMap:
    config_map_name: str


@dataclass
class _NamedSecret:
    secret_name: str


@dataclass
class BaseEnvFrom:
    """Environment variable specification from K8S resources.

    Attributes
    ----------
    prefix: str = ''
        An optional identifier to prepend to each key in the specified resources.
    """

    prefix: str = ""

    def build(self) -> EnvFromSource:
        """Constructs and returns the Argo EnvFrom specification"""
        raise NotImplementedError()


@dataclass
class SecretEnvFrom(BaseEnvFrom, _NamedSecret):
    """Environment variable specification from K8S secrets.

    Attributes
    ----------
    secret_name: str
        The name of the secret to load environments.
    optional: bool = False
        Specify whether the K8S secret must be defined
    """

    optional: bool = False

    def build(self) -> EnvFromSource:
        """Constructs and returns the Argo EnvFrom specification"""
        return EnvFromSource(
            prefix=self.prefix, secret_ref=SecretEnvSource(name=self.secret_name, optional=self.optional)
        )


@dataclass
class ConfigMapEnvFrom(BaseEnvFrom, _NamedConfigMap):
    """Environment variable specification from K8S config map.

    Attributes
    ----------
    config_map_name: str
        The name of the config map to load environments.
    optional: bool = False
        Specify whether the K8S config map must be defined
    """

    optional: bool = False

    def build(self) -> EnvFromSource:
        """Constructs and returns the Argo EnvFrom specification"""
        return EnvFromSource(
            prefix=self.prefix, config_map_ref=ConfigMapEnvSource(name=self.config_map_name, optional=self.optional)
        )
