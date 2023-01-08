import hashlib
import json
import string
from itertools import islice
from typing import Any, Optional, Union

from pydantic import root_validator, validator

from hera._base_model import BaseModel
from hera.global_config import GlobalConfig
from hera.models import ConfigMapKeySelector as _ModelConfigMapKeySelector
from hera.models import EnvVar as _ModelEnvVar
from hera.models import EnvVarSource as _ModelEnvVarSource
from hera.models import ObjectFieldSelector as _ModelObjectFieldSelector
from hera.models import Quantity
from hera.models import ResourceFieldSelector as _ModelResourceFieldSelector
from hera.models import SecretKeySelector as _ModelSecretKeySelector
from hera.parameter import Parameter


class _BaseEnv(BaseModel):
    name: str

    def build(self) -> _ModelEnvVar:
        raise NotImplementedError


class Env(_BaseEnv):
    value: Optional[Any] = None
    value_from_input: Optional[Union[str, Parameter]] = None

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
    api_version: Optional[str] = None
    field_path: str

    @validator("api_version")
    def _check_api_version(cls, v):
        if v is None:
            return GlobalConfig.api_version
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


__all__ = [*[c.__class__.__name__ for c in _BaseEnv.__subclasses__()]]
