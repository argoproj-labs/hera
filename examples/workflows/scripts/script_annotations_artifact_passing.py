"""This example will reuse the outputs volume across script steps."""

from pathlib import Path
from typing import Annotated

from hera.workflows import (
    Artifact,
    ArtifactLoader,
    Parameter,
    Steps,
    Workflow,
    script,
)


@script(constructor="runner")
def output_artifact(
    a_number: Annotated[int, Parameter(name="a_number")],
) -> Annotated[int, Artifact(name="successor_out")]:
    return a_number + 1


@script(constructor="runner")
def use_artifact(
    successor_in: Annotated[
        int,
        Artifact(name="successor_in", path="/my-path", loader=ArtifactLoader.json),
    ],
):
    print(successor_in)
    print(Path("/my-path").read_text())  # if you still need the actual path, it is still mounted where you specify


with Workflow(
    generate_name="annotations-artifact-passing",
    entrypoint="my-steps",
) as w:
    with Steps(name="my-steps") as s:
        out = output_artifact(arguments={"a_number": 3})
        use_artifact(arguments=[out.get_artifact("successor_out").with_name("successor_in")])
