import hashlib
import json
import string
from itertools import islice
from typing import Any, Optional, Union

from pydantic import root_validator, validator

from hera.shared import global_config
from hera.shared._base_model import BaseModel as _BaseModel
from hera.workflows.models import (
    ConfigMapKeySelector as _ModelConfigMapKeySelector,
    EnvVar as _ModelEnvVar,
    EnvVarSource as _ModelEnvVarSource,
    ObjectFieldSelector as _ModelObjectFieldSelector,
    Quantity,
    ResourceFieldSelector as _ModelResourceFieldSelector,
    SecretKeySelector as _ModelSecretKeySelector,
)
from hera.workflows.parameter import Parameter


class _BaseEnv(_BaseModel):
    name: str

    def __init__(self, name: str):
        self.name = name
        super().__init__()

    def build(self) -> _ModelEnvVar:
        raise NotImplementedError


class Env(_BaseEnv):
    value: Optional[Any] = None
    value_from_input: Optional[Union[str, Parameter]] = None

    def __init__(
        self, name: str, value: Optional[Any] = None, value_from_input: Optional[Union[str, Parameter]] = None
    ):
        self.value = value
        self.value_from_input = value_from_input
        super().__init__(name)

    @staticmethod
    def _sanitise_param_for_argo(v: str) -> str:
        """Argo has some strict parameter validation. To satisfy, we replace all ._ with a dash,
        take only first 32 characters from a-zA-Z0-9-, and append md5 digest of the original string."""
        # NOTE move this to some general purpose utils?
        replaced_dashes = v.translate(str.maketrans({e: "-" for e in "_."}))  # type: ignore
        legit_set = string.ascii_letters + string.digits + "-"
        legit_prefix = "".join(islice((c for c in replaced_dashes if c in legit_set), 32))
        hash_suffix = hashlib.md5(v.encode("utf-8")).hexdigest()
        return f"{legit_prefix}-{hash_suffix}"

    @root_validator(pre=True)
    def _check_values(cls, values):
        if values.get("value") is not None and values.get("value_from_input") is not None:
            raise ValueError("cannot specify both `value` and `value_from_input`")

        return values

    @property
    def param_name(self) -> str:
        if not self.value_from_input:
            raise ValueError(
                "unexpected use of `param_name` -- without value_from_input, no param should be generated"
            )
        return Env._sanitise_param_for_argo(self.name)

    def build(self) -> _ModelEnvVar:
        """Constructs and returns the Argo environment specification"""
        if self.value_from_input is not None:
            self.value = f"{{{{inputs.parameters.{self.param_name}}}}}"
        elif isinstance(self.value, str):
            self.value = self.value
        else:
            self.value = json.dumps(self.value)
        return _ModelEnvVar(name=self.name, value=self.value)


class SecretEnv(_BaseEnv):
    secret_key: str
    secret_name: Optional[str] = None
    optional: Optional[bool] = None

    def __init__(self, name: str, secret_key: str, secret_name: Optional[str] = None, optional: Optional[bool] = None):
        self.secret_key = secret_key
        self.secret_name = secret_name
        self.optional = optional
        super().__init__(name)

    def build(self) -> _ModelEnvVar:
        """Constructs and returns the Argo environment specification"""
        return _ModelEnvVar(
            name=self.name,
            value_from=_ModelEnvVarSource(
                secret_key_ref=_ModelSecretKeySelector(
                    name=self.secret_name, key=self.secret_key, optional=self.optional
                )
            ),
        )


class ConfigMapEnv(_BaseEnv):
    config_map_key: str
    config_map_name: Optional[str]
    optional: Optional[bool] = None

    def __init__(
        self, name: str, config_map_key: str, config_map_name: Optional[str] = None, optional: Optional[bool] = None
    ):
        self.config_map_key = config_map_key
        self.config_map_name = config_map_name
        self.optional = optional
        super().__init__(name)

    def build(self) -> _ModelEnvVar:
        """Constructs and returns the Argo environment specification"""
        return _ModelEnvVar(
            name=self.name,
            value_from=_ModelEnvVarSource(
                config_map_key_ref=_ModelConfigMapKeySelector(
                    name=self.config_map_name, key=self.config_map_key, optional=self.optional
                )
            ),
        )


class FieldEnv(_BaseEnv):
    field_path: str
    api_version: Optional[str] = None

    def __init__(self, name: str, field_path: str, api_version: Optional[str] = None):
        self.field_path = field_path
        self.api_version = api_version
        super().__init__(name)

    @validator("api_version")
    def _check_api_version(cls, v):
        if v is None:
            return global_config.api_version
        return v

    def build(self) -> _ModelEnvVar:
        """Constructs and returns the Argo environment specification"""
        return _ModelEnvVar(
            name=self.name,
            value_from=_ModelEnvVarSource(
                field_ref=_ModelObjectFieldSelector(
                    field_path=self.field_path,
                    api_version=self.api_version,
                )
            ),
        )


class ResourceEnv(_BaseEnv):
    resource: str
    container_name: Optional[str] = None
    divisor: Optional[Quantity] = None

    def __init__(
        self, name: str, resource: str, container_name: Optional[str] = None, divisor: Optional[Quantity] = None
    ):
        self.resource = resource
        self.container_name = container_name
        self.divisor = divisor
        super().__init__(name)

    def build(self) -> _ModelEnvVar:
        return _ModelEnvVar(
            name=self.name,
            value_from=_ModelEnvVarSource(
                resource_field_ref=_ModelResourceFieldSelector(
                    container_name=self.container_name,
                    divisor=self.divisor,
                    resource=self.resource,
                )
            ),
        )


__all__ = [*[c.__name__ for c in _BaseEnv.__subclasses__()]]
