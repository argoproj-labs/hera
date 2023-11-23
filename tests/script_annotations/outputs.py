"""Test the correctness of the Output annotations. The test inspects the inputs and outputs of the workflow."""

try:
    from typing import Annotated  # type: ignore
except ImportError:
    from typing_extensions import Annotated  # type: ignore

from pathlib import Path
from typing import Tuple

from hera.shared import global_config
from hera.workflows import Artifact, Parameter, RunnerScriptConstructor, Workflow, script
from hera.workflows.steps import Steps

global_config.experimental_features["script_annotations"] = True


@script(constructor=RunnerScriptConstructor(outputs_directory="/user/chosen/outputs"))
def custom_output_directory(
    a_number: Annotated[int, Parameter(name="a_number")],
    successor: Annotated[Path, Parameter(name="successor", output=True)],
) -> None:
    successor.write_text(str(a_number + 1))


@script(constructor="runner")
def output_artifact_as_function_parameter(
    a_number: Annotated[int, Parameter(name="a_number")],
    successor: Annotated[Path, Artifact(name="successor", output=True)],
) -> None:
    successor.write_text(a_number + 1)


@script(constructor="runner")
def output_parameter_as_function_parameter(
    a_number: Annotated[int, Parameter(name="a_number")],
    successor: Annotated[Path, Parameter(name="successor", output=True)],
) -> None:
    successor.write_text(str(a_number + 1))


@script(constructor="runner")
def output_artifact_and_parameter_as_function_parameters(
    a_number: Annotated[int, Parameter(name="a_number")],
    successor: Annotated[Path, Parameter(name="successor", output=True)],
    successor2: Annotated[Path, Artifact(name="successor2", output=True)],
) -> None:
    successor.write_text(a_number + 1)
    successor2.write_text(a_number + 2)


@script(constructor="runner")
def outputs_in_function_parameters_and_return_signature(
    a_number: Annotated[int, Parameter(name="a_number")],
    successor: Annotated[Path, Parameter(name="successor", output=True)],
    successor2: Annotated[Path, Artifact(name="successor2", output=True)],
) -> Tuple[
    Annotated[int, Parameter(name="successor3")],
    Annotated[int, Artifact(name="successor4")],
]:
    successor.write_text(a_number + 1)
    successor2.write_text(a_number + 2)
    return a_number + 3, a_number + 4


@script(constructor="runner")
def output_annotations_unnamed_in_function_parameters(
    a_number: Annotated[int, Parameter(name="a_number")],
    successor: Annotated[Path, Parameter(output=True)],
    successor2: Annotated[Path, Artifact(output=True)],
) -> None:
    successor.write_text(a_number + 1)
    successor2.write_text(a_number + 2)


with Workflow(generate_name="test-outputs-", entrypoint="my-steps") as w:
    with Steps(name="my-steps") as s:
        custom_output_directory(arguments={"a_number": 3})
        output_artifact_as_function_parameter(arguments={"a_number": 3})
        output_parameter_as_function_parameter(arguments={"a_number": 3})
        output_artifact_and_parameter_as_function_parameters(arguments={"a_number": 3})
        outputs_in_function_parameters_and_return_signature(arguments={"a_number": 3})
        output_annotations_unnamed_in_function_parameters(arguments={"a_number": 3})
