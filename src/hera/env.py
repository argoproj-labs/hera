from typing import Any, Optional

from argo_workflows.models import (
    ConfigMapKeySelector,
    EnvVar,
    EnvVarSource,
    SecretKeySelector,
)
from pydantic import BaseModel, validator

from hera.validators import json_serializable
from hera.json_utils import encode_json


class EnvSpec(BaseModel):
    """Environment variable specification for tasks.

    Attributes
    ----------
    name: str
        The name of the variable.
    value: Optional[Any] = None
        The value of the variable. This value is serialized for the client.
        This uses hera.json_utils.encode_json to encode the supplied value to
        json.
    Raises
    ------
    AssertionError
        When the specified value is not JSON serializable.
    """

    name: str
    value: Optional[Any] = None

    @validator('value')
    def check_value_json_serializable(cls, value):
        """Verifies that the specific environment value"""
        assert json_serializable(value), 'specified value is not JSON serializable'
        return value

    @property
    def argo_spec(self) -> EnvVar:
        """Constructs and returns the Argo environment specification"""
        value = encode_json(self.value)
        return EnvVar(name=self.name, value=value)


class SecretEnvSpec(EnvSpec):
    """Environment variable specification from K8S secrets.

    Attributes
    ----------
    secret_name: str
        The name of the secret to load values from.
    secret_key: str
        The key of the value within the secret.
    """

    secret_name: str
    secret_key: str

    @property
    def argo_spec(self) -> EnvVar:
        """Constructs and returns the Argo environment specification"""
        return EnvVar(
            name=self.name,
            value_from=EnvVarSource(secret_key_ref=SecretKeySelector(name=self.secret_name, key=self.secret_key)),
        )


class ConfigMapEnvSpec(EnvSpec):
    """Environment variable specification from K8S config map.

    Attributes
    ----------
    config_map_name: str
        The name of the config map to load values from.
    config_map_key: str
        The key of the value within the config map.
    """

    config_map_name: str
    config_map_key: str

    @property
    def argo_spec(self) -> EnvVar:
        """Constructs and returns the Argo environment specification"""
        return EnvVar(
            name=self.name,
            value_from=EnvVarSource(
                config_map_key_ref=ConfigMapKeySelector(name=self.config_map_name, key=self.config_map_key)
            ),
        )
