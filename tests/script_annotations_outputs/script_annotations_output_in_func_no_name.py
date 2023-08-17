"""Test the correctness of the Output annotations. The test inspects the inputs and outputs of the workflow"""

try:
    from typing import Annotated  # type: ignore
except ImportError:
    from typing_extensions import Annotated  # type: ignore

from pathlib import Path

from hera.workflows import Artifact, Parameter, Workflow, script
from hera.workflows.steps import Steps
from hera.shared import global_config


global_config.experimental_features["script_runner"] = True


@script(constructor="runner")
def script_param_in_fun_sig(
    a_number: Annotated[int, Parameter(name="a_number")],
    successor: Annotated[Path, Parameter(output=True)],
    successor2: Annotated[Path, Artifact(output=True)],
):
    successor.write_text(a_number + 1)
    successor.write_text(a_number + 2)


with Workflow(generate_name="test-outputs-", entrypoint="my_steps") as w:
    with Steps(name="my_steps") as s:
        script_param_in_fun_sig(arguments={"a_number": 3})
