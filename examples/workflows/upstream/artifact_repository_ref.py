from hera.workflows import (
    Artifact,
    Container,
    Workflow,
    models as m,
)

with Workflow(
    generate_name="artifactory-repository-ref-",
    entrypoint="main",
    artifact_repository_ref=m.ArtifactRepositoryRef(key="my-key"),
) as w:
    Container(
        name="main",
        image="docker/whalesay:latest",
        command=["sh", "-c"],
        args=["cowsay hello world | tee /tmp/hello_world.txt"],
        outputs=[Artifact(name="hello_world", path="/tmp/hello_world.txt")],
    )
