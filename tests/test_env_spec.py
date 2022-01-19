from hera.env import EnvSpec


def test_env_spec_string_value():
    env = EnvSpec(name="ENV_STRING", value='test')
    argo_spec = env.argo_spec
    assert argo_spec.value == 'test'
