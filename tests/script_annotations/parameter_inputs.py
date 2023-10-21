from typing import List

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated

from pydantic import BaseModel

from hera.shared import global_config
from hera.workflows import Parameter, Script, Steps, Workflow, script

global_config.experimental_features["script_runner"] = True
global_config.experimental_features["script_annotations"] = True


class Input(BaseModel):
    a: int
    b: str = "foo"


class Output(BaseModel):
    output: List[Input]


@script()
def annotated_basic_types(
    a_but_kebab: Annotated[int, Parameter(name="a-but-kebab")] = 2,
    b_but_kebab: Annotated[str, Parameter(name="b-but-kebab")] = "foo",
) -> Output:
    return Output(output=[Input(a=a_but_kebab, b=b_but_kebab)])


@script()
def annotated_object(annotated_input_value: Annotated[Input, Parameter(name="input-value")]) -> Output:
    return Output(output=[annotated_input_value])

@script()
def annotated_parameter_no_name(annotated_input_value: Annotated[Input, Parameter(description="a value to input")]) -> Output:
    return Output(output=[annotated_input_value])
