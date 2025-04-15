"""Test the correctness of the Output annotations. The test uses the runner to check the outputs and if they save correctly to files."""

from pathlib import Path
from typing import Annotated, Dict, List, Tuple

from tests.helper import ARTIFACT_PATH

from hera.shared import global_config
from hera.workflows import Artifact, Parameter, script

try:
    from pydantic.v1 import BaseModel
except ImportError:
    from pydantic import BaseModel

global_config.experimental_features["script_annotations"] = True


@script()
def empty_str_param() -> Annotated[str, Parameter(name="empty-str")]:
    return ""


@script()
def none_param() -> Annotated[type(None), Parameter(name="null-str")]:  # type: ignore
    return None


@script()
def script_param(a_number) -> Annotated[int, Parameter(name="successor")]:
    return a_number + 1


@script()
def script_artifact(a_number) -> Annotated[int, Artifact(name="successor")]:
    return a_number + 1


@script()
def script_artifact_path(a_number) -> Annotated[int, Artifact(name="successor", path=ARTIFACT_PATH + "/file.txt")]:
    return a_number + 1


@script()
def script_artifact_and_param(
    a_number,
) -> Tuple[Annotated[int, Parameter(name="successor")], Annotated[int, Artifact(name="successor")]]:
    return a_number + 1, a_number + 2


@script()
def script_two_params(
    a_number,
) -> Tuple[Annotated[int, Parameter(name="successor")], Annotated[int, Parameter(name="successor2")]]:
    return a_number + 1, a_number + 2


@script()
def script_two_artifacts(
    a_number,
) -> Tuple[Annotated[int, Artifact(name="successor")], Annotated[int, Artifact(name="successor2")]]:
    return a_number + 1, a_number + 2


@script()
def script_two_params_one_output(
    a_number,
) -> Tuple[Annotated[int, Parameter(name="successor")], Annotated[int, Parameter(name="successor2")]]:
    return a_number + 1


@script()
def script_param_incorrect_basic_type(a_number) -> Annotated[int, Parameter(name="successor")]:
    return "1 + a_number"


@script()
def script_param_incorrect_generic_type(a_number) -> Annotated[Dict[str, str], Parameter(name="successor")]:
    return a_number + 1


@script()
def script_param_no_name(a_number) -> Annotated[int, Parameter()]:
    return a_number + 1


@script()
def script_param_output_raises_index_error() -> Annotated[int, Parameter(name="param-output")]:
    """Raise an IndexError."""
    a_list = []
    return a_list[0]


@script()
def script_artifact_output_raises_index_error() -> Annotated[int, Artifact(name="artifact-output")]:
    """Raise an IndexError."""
    a_list = []
    return a_list[0]


@script()
def script_outputs_in_function_signature(
    a_number: Annotated[int, Parameter(name="a_number")],
    successor: Annotated[Path, Parameter(name="successor", output=True)],
    successor2: Annotated[Path, Artifact(name="successor2", output=True)],
):
    successor.write_text(str(a_number + 1))
    successor2.write_text(str(a_number + 2))


@script()
def script_outputs_in_function_signature_with_path(
    a_number: Annotated[int, Parameter(name="a_number")],
    successor: Annotated[
        Path, Parameter(name="successor", value_from={"path": ARTIFACT_PATH + "/successor"}, output=True)
    ],
    successor2: Annotated[Path, Artifact(name="successor2", path=ARTIFACT_PATH + "/successor2", output=True)],
):
    successor.write_text(str(a_number + 1))
    successor2.write_text(str(a_number + 2))


@script()
def return_list_str() -> Annotated[List[str], Parameter(name="list-of-str")]:
    return ["my", "list"]


@script()
def return_dict() -> Annotated[Dict[str, str], Parameter(name="dict-of-str")]:
    return {"my-key": "my-value"}


@script(constructor="runner")
def script_param_artifact_in_function_signature_and_return_type(
    a_number: Annotated[int, Parameter(name="a_number")],
    successor: Annotated[Path, Parameter(name="successor", output=True)],
    successor2: Annotated[Path, Artifact(name="successor2", output=True)],
) -> Tuple[Annotated[int, Parameter(name="successor3")], Annotated[int, Artifact(name="successor4")]]:
    successor.write_text(str(a_number + 1))
    successor2.write_text(str(a_number + 2))
    return a_number + 3, a_number + 4


class MyBaseModel(BaseModel):
    a: str
    b: str


@script(constructor="runner")
def return_base_model() -> Annotated[MyBaseModel, Parameter(name="base-model-output")]:
    return MyBaseModel(a="foo", b="bar")
