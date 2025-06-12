"""The `hera.workflows.env` module provides implementations of environment variable types that can be used with Argo.

`Env` classes differ from [EnvFrom](env_from.md) classes as `EnvFrom` uses a source to retrieve a variable
from, and you can only prefix the name with something. The `Env` classes can create new independent variables.
"""

import hashlib
import json
import string
from itertools import islice
from typing import Any, Optional, Union

from hera.shared import global_config
from hera.shared._pydantic import (
    BaseModel as _BaseModel,
    root_validator,
    validator,
)
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
    """Base environment variable representation."""

    name: str
    """the name of the environment variable. This is universally required irrespective of the type of env variable"""

    def build(self) -> _ModelEnvVar:
        raise NotImplementedError


class Env(_BaseEnv):
    """A variable implementation that can expose a plain `value` or `value from input` as an env variable."""

    value: Optional[Any] = None
    """the value of the environment variable"""

    value_from_input: Optional[Union[str, Parameter]] = None
    """an optional `str` or `Parameter` representation of the origin of the environment variable value"""

    @staticmethod
    def _sanitise_param_for_argo(v: str) -> str:
        """Sanitizes the given `v` value into one that satisfies Argo's parameter rules.

        Argo has some strict parameter validation. To satisfy, we replace all ._ with a dash,
        take only first 32 characters from a-zA-Z0-9-, and append md5 digest of the original string.
        """
        # NOTE move this to some general purpose utils?
        replaced_dashes = v.translate(str.maketrans({e: "-" for e in "_."}))  # type: ignore
        legit_set = string.ascii_letters + string.digits + "-"
        legit_prefix = "".join(islice((c for c in replaced_dashes if c in legit_set), 32))
        hash_suffix = hashlib.md5(v.encode("utf-8")).hexdigest()
        return f"{legit_prefix}-{hash_suffix}"

    @root_validator(pre=True)
    @classmethod
    def _check_values(cls, values):
        """Validates that only one of `value` or `value_from_input` is specified."""
        if values.get("value") is not None and values.get("value_from_input") is not None:
            raise ValueError("cannot specify both `value` and `value_from_input`")

        return values

    @property
    def param_name(self) -> str:
        """Returns the parameter name of the environment variable, conditioned on the use of `value_from_input`."""
        if not self.value_from_input:
            raise ValueError(
                "Unexpected use of `param_name` - without `value_from_input`, no param should be generated"
            )
        return Env._sanitise_param_for_argo(self.name)

    def build(self) -> _ModelEnvVar:
        """Constructs and returns the Argo environment specification."""
        if self.value_from_input is not None:
            self.value = f"{{{{inputs.parameters.{self.param_name}}}}}"
        elif isinstance(self.value, str):
            self.value = self.value
        else:
            self.value = json.dumps(self.value)
        return _ModelEnvVar(name=self.name, value=self.value)


class SecretEnv(_BaseEnv):
    """`SecretEnv` is an environment variable whose value originates from a Kubernetes secret."""

    secret_name: Optional[str] = None
    """the name of the Kubernetes secret to extract the value from"""

    secret_key: str
    """the field key within the secret that points to the value to extract and set as an env variable"""

    optional: Optional[bool] = None
    """whether the existence of the secret is optional"""

    def build(self) -> _ModelEnvVar:
        """Constructs and returns the Argo environment specification."""
        return _ModelEnvVar(
            name=self.name,
            value_from=_ModelEnvVarSource(
                secret_key_ref=_ModelSecretKeySelector(
                    name=self.secret_name, key=self.secret_key, optional=self.optional
                )
            ),
        )


class ConfigMapEnv(_BaseEnv):
    """`ConfigMapEnv` is an environment variable whose value originates from a Kubernetes config map."""

    config_map_name: Optional[str]
    """the name of the config map to reference in Kubernetes"""

    config_map_key: str
    """the name of the field key whole value should be registered as an environment variable"""

    optional: Optional[bool] = None
    """whether the existence of the config map is optional"""

    def build(self) -> _ModelEnvVar:
        """Constructs and returns the Argo environment specification."""
        return _ModelEnvVar(
            name=self.name,
            value_from=_ModelEnvVarSource(
                config_map_key_ref=_ModelConfigMapKeySelector(
                    name=self.config_map_name, key=self.config_map_key, optional=self.optional
                )
            ),
        )


class FieldEnv(_BaseEnv):
    """`FieldEnv` is an environment variable whose origin is in a field specification.

    The field path specification points to a particular field within the workflow/container YAML specification. For
    instance, if there's a YAML that has 3 fields like so
    ```
    name: abc
    spec:
      a: 42
    ```
    then a reference to the field a must be encoded as `spec.a` in order for the value of `42` to be extracted and set
    as an environment variable.
    """

    field_path: str
    """the path to the field whose value should be extracted into an environment variable"""

    api_version: Optional[str] = None
    """optionally, an API version specification. This defaults to the Hera global config `api_version`"""

    @validator("api_version")
    @classmethod
    def _check_api_version(cls, v):
        """Checks whether the `api_version` field is set and uses the global config `api_version` if not."""
        if v is None:
            return global_config.api_version
        return v

    def build(self) -> _ModelEnvVar:
        """Constructs and returns the Argo environment specification."""
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
    """`ResourceEnv` exposes a resource field as an environment variable.

    Only resources limits and requests such as `limits.cpu`, `limits.memory`, `limits.ephemeral-storage`,
    `requests.cpu`, `requests.memory` and `requests.ephemeral-storage` are currently supported.
    """

    resource: str
    """the name of the resource to select, such as `limit.cpu`, `limits.memory`, etc."""

    container_name: Optional[str] = None
    """
    a pod can contain multiple containers, so this field helps select the right container whose resources should 
    be exposed as an env variable.
    """

    divisor: Optional[Quantity] = None
    """Specifies the output format of the exposed resources, defaults to `1` on Argo's side"""

    def build(self) -> _ModelEnvVar:
        """Builds the `ResourceEnv` into a Hera auto-generated environment variable model."""
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
