from pathlib import Path
from typing import Tuple

from hera.shared import global_config
from hera.workflows import Parameter, Workflow, script
from hera.workflows.io.v1 import RunnerOutput

try:
    from typing import Annotated  # type: ignore
except ImportError:
    from typing_extensions import Annotated  # type: ignore

global_config.experimental_features["script_annotations"] = True
global_config.experimental_features["script_pydantic_io"] = True


class ParamOnlyOutput(RunnerOutput):
    my_output_str: str = "my-default-str"
    another_output: Annotated[Path, Parameter(name="second-output")]


@script(constructor="runner")
def pydantic_output_parameters_in_tuple() -> Tuple[ParamOnlyOutput, Annotated[int, Parameter(name="inline-output")]]:
    outputs = ParamOnlyOutput(annotated_str="my-val")
    outputs.my_output_str = "a string!"

    return outputs, 42


with Workflow(generate_name="pydantic-invalid-outputs-") as w:
    pydantic_output_parameters_in_tuple()
