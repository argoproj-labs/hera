from pathlib import Path
from typing import Annotated, List

from hera.workflows import Artifact, ArtifactLoader, Parameter, Workflow, script
from hera.workflows.io.v1 import Input, Output


class ParamOnlyInput(Input):
    my_int: int = 1
    my_annotated_int: Annotated[int, Parameter(name="another-int", description="my desc")] = 42
    no_default_param: int


class ParamOnlyOutput(Output):
    my_output_str: str = "my-default-str"
    another_output: Annotated[Path, Parameter(name="second-output")]
    annotated_output: Annotated[str, Parameter(description="use the field name directly")]


@script(constructor="runner")
def pydantic_io_params(
    my_input: ParamOnlyInput,
) -> ParamOnlyOutput:
    pass


class ArtifactOnlyInput(Input):
    my_file_artifact: Annotated[Path, Artifact(name="file-artifact")]
    my_int_artifact: Annotated[
        int, Artifact(name="an-int-artifact", description="my desc", loader=ArtifactLoader.json)
    ]


class ArtifactOnlyOutput(Output):
    an_artifact: Annotated[str, Artifact(name="artifact-output")]


@script(constructor="runner")
def pydantic_io_artifacts(
    my_input: ArtifactOnlyInput,
) -> ArtifactOnlyOutput:
    pass


class BothInput(Input):
    param_int: Annotated[int, Parameter(name="param-int")] = 42
    artifact_int: Annotated[int, Artifact(name="artifact-int", loader=ArtifactLoader.json)]


class BothOutput(Output):
    param_int: Annotated[int, Parameter(name="param-int")]
    artifact_int: Annotated[int, Artifact(name="artifact-int")]


@script(constructor="runner")
def pydantic_io(
    my_input: BothInput,
) -> BothOutput:
    pass


@script(constructor="runner")
def pydantic_io_with_defaults(
    my_input: ParamOnlyInput = ParamOnlyInput(my_int=2, my_annotated_int=24, no_default_param=1),
) -> ParamOnlyOutput:
    pass


@script(constructor="runner")
def pydantic_io_within_generic(
    my_inputs: List[ParamOnlyInput] = [
        ParamOnlyInput(no_default_param=1),
        ParamOnlyInput(my_int=2, no_default_param=2),
    ],
) -> ParamOnlyOutput:
    pass


with Workflow(generate_name="pydantic-io-") as w:
    pydantic_io_params()
    pydantic_io_artifacts()
    pydantic_io()
    pydantic_io_with_defaults()
    pydantic_io_within_generic()
