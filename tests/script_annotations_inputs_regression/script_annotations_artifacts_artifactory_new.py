"""Regression test: compare the new Annotated style inputs declaration with the old version."""

try:
    from typing import Annotated  # type: ignore
except ImportError:
    from typing_extensions import Annotated  # type: ignore

from hera.shared import global_config
from hera.workflows import Workflow, script
from hera.workflows.artifact import Artifact, ArtifactoryArtifact
from hera.workflows.steps import Steps

global_config.experimental_features["script_annotations"] = True


@script()
def read_artifact(
    my_artifact: Annotated[
        str,
        ArtifactoryArtifact(
            name="my_artifact",
            path="/tmp/file",
            url="http://artifactory:8081/artifactory/generic-local/hello_world.tgz",
            password_secret={"name": "my-artifactory-credentials", "key": "secretPassword"},
            username_secret={"name": "my-artifactory-credentials", "key": "secretUsername"},
        ),
    ]
) -> str:
    return my_artifact


with Workflow(generate_name="test-artifacts-", entrypoint="my-steps") as w:
    with Steps(name="my-steps") as s:
        read_artifact(arguments=[Artifact(name="my_artifact", from_="somewhere")])
