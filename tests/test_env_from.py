from hera.env_from import ConfigMapEnvFromSpec, SecretEnvFromSpec


def test_config_map_env_from_sets_name():
    env_from = ConfigMapEnvFromSpec(config_map_name='str')
    env_spec = env_from.argo_spec
    assert env_spec.prefix == ''
    assert env_spec.config_map_ref.name == 'str'
    assert env_spec.config_map_ref.optional == False


def test_secret_map_env_from_sets_name():
    env_from = SecretEnvFromSpec(prefix='p', secret_name='str', optional=True)
    env_spec = env_from.argo_spec
    assert env_spec.prefix == 'p'
    assert env_spec.secret_ref.name == 'str'
    assert env_spec.secret_ref.optional == True
