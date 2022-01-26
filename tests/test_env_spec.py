from hera.env import EnvSpec
import json
from pydantic import BaseModel


class MockModel(BaseModel):
    field1: int = 1
    field2: int = 2


def test_env_spec_sets_base_model(mock_model):
    m = mock_model()
    env = EnvSpec(name="model_string", value=m)
    argo_spec = env.argo_spec
    assert argo_spec.value == '{"field1": 1, "field2": 2}'
    model_dict = json.loads(argo_spec.value)
    test_model = MockModel(**model_dict)
    assert test_model.field1 == m.field1
    assert test_model.field2 == m.field2


def test_env_spec_sets_primitive_types_as_expected():
    int_val = 1
    int_env = EnvSpec(name="int", value=int_val)
    int_spec = int_env.argo_spec
    assert int_spec.value == '1'
    assert json.loads(int_spec.value) == int_val

    # values are stringified to env variable values, but strings are already stringified
    # so the test here ensures that strings are passed as strings, by comparison to
    # other primitive types
    str_val = 'str'
    str_env = EnvSpec(name="str", value=str_val)
    str_spec = str_env.argo_spec
    assert str_spec.value == 'str'

    dict_val = {'a': 42}
    dict_env = EnvSpec(name="dict", value=dict_val)
    dict_spec = dict_env.argo_spec
    assert dict_spec.value == '{"a": 42}'
    assert json.loads(dict_spec.value) == dict_val
