"""Compare this example to [Basic Artifacts](../artifacts/basic-artifacts.md) to see how the Hera runner simplifies your Artifact code."""

from typing import Annotated

from hera.workflows import (
    DAG,
    Artifact,
    NoneArchiveStrategy,
    Workflow,
    script,
)
from hera.workflows.artifact import ArtifactLoader


@script()
def writer() -> Annotated[str, Artifact(name="out-art", archive=NoneArchiveStrategy())]:
    return "Hello, world!"


@script()
def consumer(
    in_art: Annotated[
        str,
        Artifact(loader=ArtifactLoader.json),
    ],
):
    print(in_art)  # prints `Hello, world!` to `stdout`


with Workflow(generate_name="artifact-", entrypoint="d") as w:
    with DAG(name="d"):
        w_ = writer()
        c = consumer(arguments={"in_art": w_.get_artifact("out-art")})
        w_ >> c
