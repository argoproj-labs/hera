from hera.workflows import (
    Artifact,
    ArtifactoryArtifact,
    Container,
    Step,
    Steps,
    Workflow,
    models as m,
)

with Workflow(generate_name="artifactory-artifact-", entrypoint="artifact-example") as w:
    whalesay = Container(
        name="whalesay",
        image="docker/whalesay:latest",
        command=["sh", "-c"],
        args=["cowsay hello world | tee /tmp/hello_world.txt"],
        outputs=[
            ArtifactoryArtifact(
                name="hello-art",
                path="/tmp/hello_world.txt",
                url="http://artifactory:8081/artifactory/generic-local/hello_world.tgz",
                username_secret=m.SecretKeySelector(name="my-artifactory-credentials", key="username"),
                password_secret=m.SecretKeySelector(name="my-artifactory-credentials", key="password"),
            )
        ],
    )
    print_message = Container(
        name="print-message",
        image="alpine:latest",
        command=["sh", "-c"],
        args=["cat /tmp/message"],
        inputs=[
            ArtifactoryArtifact(
                name="message",
                path="/tmp/message",
                url="http://artifactory:8081/artifactory/generic-local/hello_world.tgz",
                username_secret=m.SecretKeySelector(name="my-artifactory-credentials", key="username"),
                password_secret=m.SecretKeySelector(name="my-artifactory-credentials", key="password"),
            )
        ],
    )

    with Steps(name="artifact-example") as s:
        generator = Step(name="generate-artifact", template=whalesay)
        Step(
            name="consume-artifact",
            template=print_message,
            arguments=[Artifact(name="message", from_=generator.outputs.artifacts.hello_art)],
        )
