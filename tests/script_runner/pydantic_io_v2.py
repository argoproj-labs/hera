from pathlib import Path
from typing import Annotated, List

from pydantic import BaseModel
from tests.helper import ARTIFACT_PATH

from hera.shared import global_config
from hera.workflows import Artifact, ArtifactLoader, Parameter, script

try:
    from hera.workflows.io.v2 import Input, Output
except ImportError:
    from hera.workflows.io.v1 import Input, Output

global_config.experimental_features["script_annotations"] = True
global_config.experimental_features["script_pydantic_io"] = True


class ParamOnlyInput(Input):
    my_required_int: int
    my_int: int = 1
    my_annotated_int: Annotated[int, Parameter(description="my desc")] = 42
    my_ints: Annotated[List[int], Parameter(name="multiple-ints")] = []


class ParamOnlyOutput(Output):
    my_output_str: str = "my-default-str"
    annotated_str: Annotated[str, Parameter(name="second-output")]
    annotated_output: Annotated[str, Parameter(description="use the field name directly")] = "test"


@script(constructor="runner")
def pydantic_input_parameters(
    my_input: ParamOnlyInput,
) -> int:
    return 42


@script(constructor="runner")
def pydantic_io_in_generic(
    my_inputs: List[ParamOnlyInput],
) -> str:
    """my_inputs is a `list` type, we cannot infer its sub-type in the runner
    so it should behave like a normal Pydantic input class.
    """
    return len(my_inputs)


@script(constructor="runner")
def pydantic_output_parameters() -> ParamOnlyOutput:
    outputs = ParamOnlyOutput(annotated_str="my-val")
    outputs.my_output_str = "a string!"

    return outputs


@script(constructor="runner")
def pydantic_output_using_exit_code() -> ParamOnlyOutput:
    outputs = ParamOnlyOutput(exit_code=42, annotated_str="my-val")
    outputs.my_output_str = "a string!"

    return outputs


@script(constructor="runner")
def pydantic_output_using_result() -> ParamOnlyOutput:
    outputs = ParamOnlyOutput(result=42, annotated_str="my-val")
    outputs.my_output_str = "a string!"

    return outputs


class MyArtifact(BaseModel):
    a: int = 42
    b: str = "b"


class ArtifactOnlyInput(Input):
    json_artifact: Annotated[MyArtifact, Artifact(loader=ArtifactLoader.json)]
    path_artifact: Annotated[Path, Artifact(name="path-artifact", path=ARTIFACT_PATH + "/path", loader=None)]
    str_path_artifact: Annotated[
        str, Artifact(name="str-path-artifact", path=ARTIFACT_PATH + "/str-path", loader=None)
    ]
    file_artifact: Annotated[
        str, Artifact(name="file-artifact", path=ARTIFACT_PATH + "/file", loader=ArtifactLoader.file)
    ]


class ArtifactOnlyOutput(Output):
    an_artifact: Annotated[str, Artifact(name="artifact-str-output")]
    another_artifact: Annotated[str, Artifact()]


@script(constructor="runner")
def pydantic_input_artifact(
    my_input: ArtifactOnlyInput,
) -> str:
    return my_input.json_artifact


@script(constructor="runner")
def pydantic_output_artifact() -> ArtifactOnlyOutput:
    return ArtifactOnlyOutput(an_artifact="test", another_artifact="test2")
