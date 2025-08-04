"""This example showcases how to run a init_containers with env"""

from hera.workflows import Container, Env, SecretEnv, UserContainer, Workflow

with Workflow(generate_name="container-", entrypoint="cowsay") as w:
    Container(
        name="cowsay",
        image="argoproj/argosay:v2",
        command=["cowsay", "foo"],
        init_containers=[
            UserContainer(
                name="init",
                image="busybox",
                command=[
                    "sh",
                    "-c",
                    "echo Hello from the init container ($FOO, $SECRET)",
                ],
                env=[
                    Env(name="FOO", value="bar"),
                    SecretEnv(name="SECRET", secret_key="password", secret_name="my-secret"),
                ],
            )
        ],
    )
