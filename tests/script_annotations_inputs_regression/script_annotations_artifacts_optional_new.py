"""Regression test: compare the new Annotated style inputs declaration with the old version."""

from typing import Annotated, Optional

from hera.workflows import Workflow, script
from hera.workflows.artifact import Artifact
from hera.workflows.steps import Steps


@script()
def read_artifact(my_artifact: Annotated[Optional[str], Artifact(name="my_artifact", path="/tmp/file")]):
    pass


with Workflow(generate_name="test-artifacts-", entrypoint="my-steps") as w:
    with Steps(name="my-steps") as s:
        read_artifact(arguments=[Artifact(name="my_artifact", from_="somewhere")])
