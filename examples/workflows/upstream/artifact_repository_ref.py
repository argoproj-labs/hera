from hera.workflows import (
    Artifact,
    Container,
    Workflow,
    models as m,
)

with Workflow(
    generate_name="artifact-repository-ref-",
    entrypoint="main",
    artifact_repository_ref=m.ArtifactRepositoryRef(key="my-key"),
) as w:
    Container(
        name="main",
        image="busybox",
        command=["sh", "-c"],
        args=["echo hello world | tee /tmp/hello_world.txt"],
        outputs=[Artifact(name="hello_world", path="/tmp/hello_world.txt")],
    )
