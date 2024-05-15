from typing_extensions import Annotated

from hera.shared import global_config
from hera.workflows import Artifact, Input, Output, Workflow

global_config.experimental_features["script_annotations"] = True
global_config.experimental_features["script_pydantic_io"] = True
global_config.experimental_features["decorator_syntax"] = True


w = Workflow(generate_name="my-workflow-")


class ArtifactOutput(Output):
    an_artifact: Annotated[str, Artifact(name="an-artifact")]


class ConcatInput(Input):
    word_a: Annotated[str, Artifact(name="word_a")]
    word_b: Annotated[str, Artifact(name="word_b")]


@w.script()
def concat(concat_input: ConcatInput) -> ArtifactOutput:
    return ArtifactOutput(an_artifact=f"{concat_input.word_a} {concat_input.word_b}")


class WorkerInput(Input):
    artifact_a: Annotated[str, Artifact(name="artifact_a")]
    artifact_b: Annotated[str, Artifact(name="artifact_b")]


@w.set_entrypoint
@w.dag()
def worker(worker_input: WorkerInput) -> ArtifactOutput:
    concat_1 = concat(
        ConcatInput(
            word_a=worker_input.artifact_a,
            word_b=worker_input.artifact_b,
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
