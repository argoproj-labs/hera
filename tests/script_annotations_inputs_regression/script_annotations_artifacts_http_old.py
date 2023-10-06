"""Regression test: compare the new Annotated style inputs declaration with the old version."""

from hera.workflows import Workflow, script
from hera.workflows.artifact import Artifact, HTTPArtifact
from hera.workflows.steps import Steps


@script(
    inputs=[
        HTTPArtifact(
            name="my_artifact",
            path="/tmp/file",
            url="https://storage.googleapis.com/kubernetes-release/release/v1.8.0/bin/linux/amd64/kubectl",
            auth={"name": "http-auth", "key": "http-key"},
            headers=[{"name": "header1", "value": "value1"}, {"name": "header2", "value": "value1"}],
        )
    ]
)
def read_artifact(my_artifact) -> str:
    return my_artifact


with Workflow(generate_name="test-artifacts-", entrypoint="my-steps") as w:
    with Steps(name="my-steps") as s:
        read_artifact(arguments=[Artifact(name="my_artifact", from_="somewhere")])
