"""This example shows how to pass Artifacts between scripts in a dag, using the new decorators.

The DAG decorator function can easily lift out an output artifact from a task as an output of the
DAG itself by referencing it in an `Output` class.
"""

from typing_extensions import Annotated

from hera.shared import global_config
from hera.workflows import (
    Artifact,
    ArtifactLoader,
    Input,
    NoneArchiveStrategy,
    Output,
    Workflow,
)

global_config.experimental_features["decorator_syntax"] = True


w = Workflow(generate_name="artifact-workflow-")


class ArtifactOutput(Output):
    an_artifact: Annotated[str, Artifact(name="an-artifact", archive=NoneArchiveStrategy())]


class ConcatInput(Input):
    word_a: Annotated[str, Artifact(name="word_a", loader=ArtifactLoader.file)]
    word_b: Annotated[str, Artifact(name="word_b", loader=ArtifactLoader.file)]


@w.script()
def create_artifact() -> ArtifactOutput:
    return ArtifactOutput(an_artifact="hello world")


@w.script()
def concat(concat_input: ConcatInput) -> ArtifactOutput:
    return ArtifactOutput(an_artifact=f"{concat_input.word_a} {concat_input.word_b}")


class WorkerInput(Input):
    artifact_a: Annotated[str, Artifact(name="artifact_a")]
    artifact_b: Annotated[str, Artifact(name="artifact_b")]


@w.set_entrypoint
@w.dag()
def worker() -> ArtifactOutput:
    create = create_artifact()
    concat_1 = concat(
        ConcatInput(
            word_a=create.an_artifact,
            word_b=create.an_artifact,
        )
    )

    concat_2 = concat(
        ConcatInput(
            word_a=concat_1.an_artifact,
            word_b=concat_1.an_artifact,
        ),
        name="concat-2-custom-name",
    )

    return ArtifactOutput(an_artifact=concat_2.an_artifact)
