from hera.workflows import (
    ConfigMapEnv,
    ConfigMapEnvFrom,
    Container,
    Env,
    ResourceEnv,
    SecretEnv,
    SecretEnvFrom,
    Workflow,
)

with Workflow(generate_name="secret-env-from-", entrypoint="whalesay") as w:
    whalesay = Container(
        name="whalesay",
        image="docker/whalesay:latest",
        command=["cowsay"],
        env_from=[
            SecretEnvFrom(prefix="abc", name="secret", optional=False),
            ConfigMapEnvFrom(prefix="abc", name="configmap", optional=False),
        ],
        env=[
            Env(name="test", value="1"),
            SecretEnv(name="s1", secret_key="s1", secret_name="abc"),
            ResourceEnv(name="r1", resource="abc"),
            ConfigMapEnv(name="c1", config_map_key="c1", config_map_name="abc"),
        ],
    )
