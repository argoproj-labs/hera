# def test_get_var_from_spec_returns_aws_creds():
#     specs = get_var_from_spec(Env.AWS)
#     assert len(specs) == 2, 'expected only 2 keys for aws'
#     assert specs[0].name == 'AWS_ACCESS_KEY_ID', 'unexpected key name specification for aws'
#     assert specs[1].name == 'AWS_SECRET_ACCESS_KEY', 'unexpected secret name specification for aws'
#     assert specs[0].value_from.secret_key_ref.name == 'aws-credentials', 'invalid k8s secret reference'
#     assert specs[1].value_from.secret_key_ref.name == 'aws-credentials', 'invalid k8s secret reference'
#
#
# def test_get_var_from_spec_returns_empty():
#     specs = get_var_from_spec(None)
#     assert not specs
#
#
# def test_get_var_multi_returns_multi_env_var():
#     specs = get_vars_from_specs([Env.AWS, Env.AWS])
#     assert len(specs) == 4
#     assert all([isinstance(x, V1EnvVar) for x in specs])
