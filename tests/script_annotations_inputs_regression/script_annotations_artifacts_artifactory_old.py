"""Regression test: compare the new Annotated style inputs declaration with the old version."""

from hera.workflows import Workflow, script
from hera.workflows.artifact import Artifact, ArtifactoryArtifact
from hera.workflows.steps import Steps


@script(
    inputs=[
        ArtifactoryArtifact(
            name="my_artifact",
            path="/tmp/file",
            url="http://artifactory:8081/artifactory/generic-local/hello_world.tgz",
            password_secret={"name": "my-artifactory-credentials", "key": "secretPassword"},
            username_secret={"name": "my-artifactory-credentials", "key": "secretUsername"},
        )
    ]
)
def read_artifact(my_artifact) -> str:
    return my_artifact


with Workflow(generate_name="test-artifacts-", entrypoint="my-steps") as w:
    with Steps(name="my-steps") as s:
        read_artifact(arguments=[Artifact(name="my_artifact", from_="somewhere")])
