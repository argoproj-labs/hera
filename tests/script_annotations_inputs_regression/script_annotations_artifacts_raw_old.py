"""Regression test: compare the new Annotated style inputs declaration with the old version."""

from hera.workflows import Workflow, script
from hera.workflows.artifact import Artifact, RawArtifact
from hera.workflows.steps import Steps


@script(
    inputs=[
        RawArtifact(
            name="my_artifact",
            path="/tmp/file",
            data="""this is
            the raw file
            contents""",
        ),
    ]
)
def read_artifact(my_artifact) -> str:
    return my_artifact


with Workflow(generate_name="test-artifacts-", entrypoint="my-steps") as w:
    with Steps(name="my-steps") as s:
        read_artifact(arguments=[Artifact(name="my_artifact", from_="somewhere")])
