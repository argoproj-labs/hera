import json

from argo_workflows.model.object_field_selector import ObjectFieldSelector
from argo_workflows.models import ConfigMapKeySelector, EnvVarSource, SecretKeySelector

from hera.workflows import ConfigMapEnv, Env, FieldEnv, SecretEnv


def test_env_spec_sets_primitive_types_as_expected():
    int_val = 1
    int_env = Env(name="int", value=int_val)
    int_spec = int_env.build()
    assert int_spec.value == "1"
    assert json.loads(int_spec.value) == int_val

    # values are stringified to env variable values, but strings are already stringified
    # so the test here ensures that strings are passed as strings, by comparison to
    # other primitive types
    str_val = "str"
    str_env = Env(name="str", value=str_val)
    str_spec = str_env.build()
    assert str_spec.value == "str"

    dict_val = {"a": 42}
    dict_env = Env(name="dict", value=dict_val)
    dict_spec = dict_env.build()
    assert dict_spec.value == '{"a": 42}'
    assert json.loads(dict_spec.value) == dict_val


def test_secret_env_spec_contains_expected_fields():
    env = SecretEnv(name="s", secret_name="a", secret_key="b")
    spec = env.build()

    assert not hasattr(spec, "value")
    assert spec.name == "s"
    assert isinstance(spec.value_from, EnvVarSource)
    assert isinstance(spec.value_from.secret_key_ref, SecretKeySelector)
    assert spec.value_from.secret_key_ref.name == "a"
    assert spec.value_from.secret_key_ref.key == "b"


def test_config_map_env_spec_contains_expected_fields():
    env = ConfigMapEnv(name="s", config_map_name="a", config_map_key="b")
    spec = env.build()

    assert not hasattr(spec, "value")
    assert spec.name == "s"
    assert isinstance(spec.value_from, EnvVarSource)
    assert isinstance(spec.value_from.config_map_key_ref, ConfigMapKeySelector)
    assert spec.value_from.config_map_key_ref.name == "a"
    assert spec.value_from.config_map_key_ref.key == "b"


def test_field_env_spec_contains_expected_fields():
    env = FieldEnv(name="s", field_path="a", api_version="b")
    spec = env.build()

    assert not hasattr(spec, "value")
    assert spec.name == "s"
    assert isinstance(spec.value_from, EnvVarSource)
    assert isinstance(spec.value_from.field_ref, ObjectFieldSelector)
    assert spec.value_from.field_ref.field_path == "a"
    assert spec.value_from.field_ref.api_version == "b"
