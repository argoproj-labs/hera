"""Test the correctness of the Output annotations. The test uses the runner to check the outputs and if they save correctly to files."""

try:
    from typing import Annotated  # type: ignore
except ImportError:
    from typing_extensions import Annotated  # type: ignore

from pathlib import Path
from typing import Tuple

from tests.helper import ARTIFACT_PATH

from hera.workflows import Artifact, Parameter, Workflow, script
from hera.shared import global_config
from hera.workflows.steps import Steps


global_config.experimental_features["script_runner"] = True


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
def script_param_incorrect_type(a_number) -> Annotated[int, Parameter(name="successor")]:
    return "1 + a_number"


@script()
def script_param_no_name(a_number) -> Annotated[int, Parameter()]:
    return a_number + 1


@script(constructor="runner")
def script_param_in_function_signature(
    a_number: Annotated[int, Parameter(name="a_number")],
    successor: Annotated[Path, Parameter(name="successor", output=True)],
):
    successor.write_text(a_number + 1)


with Workflow(generate_name="test-outputs-", entrypoint="my_steps") as w:
    with Steps(name="my_steps") as s:
        script_param(arguments={"a_number": 3})
        script_artifact(arguments={"a_number": 3})
        script_artifact_path(arguments={"a_number": 3})
        script_artifact_and_param(arguments={"a_number": 3})
        script_two_params(arguments={"a_number": 3})
        script_two_artifacts(arguments={"a_number": 3})
