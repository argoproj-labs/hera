import json
from typing import Any, Optional

from argo.workflows.client import (
    V1ConfigMapKeySelector,
    V1EnvVar,
    V1EnvVarSource,
    V1SecretKeySelector,
)
from pydantic import BaseModel, validator

from hera.validators import json_serializable


class EnvSpec(BaseModel):
    """Environment variable specification for tasks.

    Attributes
    ----------
    name: str
        The name of the variable.
    value: Optional[Any] = None
        The value of the variable. This value is serialized for the client. If a pydantic BaseModel is passed in the
        corresponding `.json()` method will be used for serialization. It is up to the client to deserialize the value
        in the task. In addition, if another type is passed, covered by `Any`, an attempt at `json.dumps` will be
        performed.

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
    def argo_spec(self) -> V1EnvVar:
        """Constructs and returns the Argo environment specification"""
        if isinstance(self.value, BaseModel):
            value = self.value.json()
        elif isinstance(self.value, str):
            value = self.value
        else:
            value = json.dumps(self.value)
        return V1EnvVar(name=self.name, value=value)


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
    def argo_spec(self) -> V1EnvVar:
        """Constructs and returns the Argo environment specification"""
        return V1EnvVar(
            name=self.name,
            value_from=V1EnvVarSource(secret_key_ref=V1SecretKeySelector(name=self.secret_name, key=self.secret_key)),
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
    def argo_spec(self) -> V1EnvVar:
        """Constructs and returns the Argo environment specification"""
        return V1EnvVar(
            name=self.name,
            value_from=V1EnvVarSource(
                config_map_key_ref=V1ConfigMapKeySelector(name=self.config_map_name, key=self.config_map_key)
            ),
        )
