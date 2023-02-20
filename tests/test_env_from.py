from hera.workflows import ConfigMapEnvFrom, SecretEnvFrom


def test_config_map_env_from_sets_name():
    env_from = ConfigMapEnvFrom(config_map_name="str")
    env_spec = env_from.build()
    assert env_spec.prefix == ""
    assert env_spec.config_map_ref.name == "str"
    assert env_spec.config_map_ref.optional == False


def test_secret_map_env_from_sets_name():
    env_from = SecretEnvFrom(prefix="p", secret_name="str", optional=True)
    env_spec = env_from.build()
    assert env_spec.prefix == "p"
    assert env_spec.secret_ref.name == "str"
    assert env_spec.secret_ref.optional == True
