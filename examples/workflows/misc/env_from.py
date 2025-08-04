from hera.workflows import ConfigMapEnvFrom, Container, SecretEnvFrom, Workflow

with Workflow(generate_name="secret-env-from-", entrypoint="whalesay") as w:
    whalesay = Container(
        name="whalesay",
        image="argoproj/argosay:v2",
        command=["cowsay"],
        env_from=[
            SecretEnvFrom(prefix="abc", name="secret", optional=False),
            ConfigMapEnvFrom(prefix="abc", name="configmap", optional=False),
        ],
    )
