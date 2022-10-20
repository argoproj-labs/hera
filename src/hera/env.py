import hashlib
import json
import string
from dataclasses import dataclass
from itertools import islice
from typing import Any, Optional, Union

from argo_workflows.models import (
    ConfigMapKeySelector,
    EnvVar,
    EnvVarSource,
    ObjectFieldSelector,
    SecretKeySelector,
)

from hera.parameter import Parameter


@dataclass
class ConfigMapNamedKey:
    """Config map representation. Supports the specification of a name/key string pair to identify a value"""

    config_map_name: str
    config_map_key: str


@dataclass
class SecretNamedKey:
    """Secret map representation. Supports the specification of a name/key string pair to identify a value"""

    secret_name: str
    secret_key: str


@dataclass
class Env:
    """Environment variable specification for tasks.

    Attributes
    ----------
    name: str
        The name of the variable.
    value: Optional[Any] = None
        The value of the variable. This value is serialized for the client. It is up to the client to deserialize the
        value in the task. In addition, if another type is passed, covered by `Any`, an attempt at `json.dumps` will be
        performed.
    value_from_input: Optional[Union[str, Parameter]] = None
        An external reference which will resolve the env-value, E.g. another task's output parameter.
        An input parameter will be auto-generated for the task the `Env` is instantiated in.

    Raises
    ------
    AssertionError
        When the specified value is not JSON serializable.
    """

    name: str
    value: Optional[Any] = None
    value_from_input: Optional[Union[str, Parameter]] = None

    @staticmethod
    def _sanitise_param_for_argo(v: str) -> str:
        """Argo has some strict parameter validation. To satisfy, we replace all ._ with a dash,
        take only first 32 characters from a-zA-Z0-9-, and append md5 digest of the original string."""
        # NOTE move this to some general purpose utils?
        replaced_dashes = v.translate(str.maketrans({e: '-' for e in "_."}))  # type: ignore
        legit_set = string.ascii_letters + string.digits + '-'
        legit_prefix = "".join(islice((c for c in replaced_dashes if c in legit_set), 32))
        hash_suffix = hashlib.md5(v.encode("utf-8")).hexdigest()
        return f"{legit_prefix}-{hash_suffix}"

    @property
    def param_name(self) -> str:
        if not self.value_from_input:
            raise ValueError(
                "unexpected use of `param_name` -- without value_from_input, no param should be generated"
            )
        return Env._sanitise_param_for_argo(self.name)

    def __post_init__(self):
        if self.value is not None and self.value_from_input is not None:
            raise ValueError("cannot specify both value and value_from_input")

    def build(self) -> EnvVar:
        """Constructs and returns the Argo environment specification"""
        if self.value_from_input is not None:
            value = f"{{{{inputs.parameters.{self.param_name}}}}}"
        elif isinstance(self.value, str):
            value = self.value
        else:
            value = json.dumps(self.value)
        return EnvVar(name=self.name, value=value)


@dataclass
class SecretEnv(Env, SecretNamedKey):
    """Environment variable specification from K8S secrets.

    Attributes
    ----------
    secret_name: str
        The name of the secret to load values from.
    secret_key: str
        The key of the value within the secret.
    """

    def build(self) -> EnvVar:
        """Constructs and returns the Argo environment specification"""
        return EnvVar(
            name=self.name,
            value_from=EnvVarSource(secret_key_ref=SecretKeySelector(name=self.secret_name, key=self.secret_key)),
        )


@dataclass
class ConfigMapEnv(Env, ConfigMapNamedKey):
    """Environment variable specification from K8S config map.

    Attributes
    ----------
    config_map_name: str
        The name of the config map to load values from.
    config_map_key: str
        The key of the value within the config map.
    """

    def build(self) -> EnvVar:
        """Constructs and returns the Argo environment specification"""
        return EnvVar(
            name=self.name,
            value_from=EnvVarSource(
                config_map_key_ref=ConfigMapKeySelector(name=self.config_map_name, key=self.config_map_key)
            ),
        )


@dataclass
class FieldPath:
    """Field path representation.

    This allows obtaining K8S values via indexing into specific fields of the K8S definition.

    Attributes
    ----------
    field_path: str
        Path to the field to obtain the value from.
    """

    field_path: str


@dataclass
class FieldEnv(Env, FieldPath):
    """Environment variable specification from K8S object field.

    Attributes
    ----------
    name: str
        The name of the variable.
    value: Optional[Any] = None
        The value of the variable. This value is serialized for the client. It is up to the client to deserialize the
        value in the task. In addition, if another type is passed, covered by `Any`, an attempt at `json.dumps` will be
        performed.
    value_from_input: Optional[str] = None
        A reference to an input parameter which will resolve to the value. The input parameter will be auto-generated.
    field_path: str
        Path to the field to obtain the value from.
    api_version: Optional[str] = 'v1'
        The version of the schema the FieldPath is written in terms of. Defaults to 'v1'.
    """

    api_version: Optional[str] = "v1"

    def build(self) -> EnvVar:
        """Constructs and returns the Argo environment specification"""
        return EnvVar(
            name=self.name,
            value_from=EnvVarSource(
                field_ref=ObjectFieldSelector(field_path=self.field_path, api_version=self.api_version)
            ),
        )
