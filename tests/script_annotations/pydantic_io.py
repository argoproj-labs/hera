from pathlib import Path

from hera.shared import global_config
from hera.workflows import Artifact, ArtifactLoader, Parameter, Workflow, script
from hera.workflows.io import RunnerInput, RunnerOutput

try:
    from typing import Annotated  # type: ignore
except ImportError:
    from typing_extensions import Annotated  # type: ignore

global_config.experimental_features["script_annotations"] = True
global_config.experimental_features["script_pydantic_io"] = True


class ParamOnlyInput(RunnerInput):
    my_int: int = 1
    my_annotated_int: Annotated[int, Parameter(name="another-int", description="my desc")] = 42


class ParamOnlyOutput(RunnerOutput):
    my_output_str: str = "my-default-str"
    another_output: Annotated[Path, Parameter(name="second-output")]


@script(constructor="runner")
def pydantic_io_params(
    my_input: ParamOnlyInput,
    another_param_inline: int,
    another_annotated_param_inline: Annotated[str, Parameter(name="a-str-param")],
) -> ParamOnlyOutput:
    pass


class ArtifactOnlyInput(RunnerInput):
    my_file_artifact: Annotated[Path, Artifact(name="file-artifact")]
    my_int_artifact: Annotated[
        int, Artifact(name="an-int-artifact", description="my desc", loader=ArtifactLoader.json)
    ]


class ArtifactOnlyOutput(RunnerOutput):
    an_artifact: Annotated[str, Artifact(name="artifact-output")]


@script(constructor="runner")
def pydantic_io_artifacts(
    my_input: ArtifactOnlyInput,
    annotated_artifact_inline: Annotated[str, Artifact(name="inline-artifact")],
) -> ArtifactOnlyOutput:
    pass


class BothInput(RunnerInput):
    param_int: Annotated[int, Parameter(name="param-int")] = 42
    artifact_int: Annotated[int, Artifact(name="artifact-int", loader=ArtifactLoader.json)]


class BothOutput(RunnerOutput):
    param_int: Annotated[int, Parameter(name="param-int")]
    artifact_int: Annotated[int, Artifact(name="artifact-int")]


@script(constructor="runner")
def pydantic_io(
    my_input: BothInput,
) -> BothOutput:
    pass


with Workflow(generate_name="pydantic-io-") as w:
    pydantic_io_params()
    pydantic_io_artifacts()
    pydantic_io()
