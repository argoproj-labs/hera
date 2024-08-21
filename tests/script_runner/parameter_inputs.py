import json
from typing import Any, List

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated

from pydantic import BaseModel

try:
    from pydantic.v1 import BaseModel as V1BaseModel
except (ImportError, ModuleNotFoundError):
    from pydantic import BaseModel as V1BaseModel

from hera.shared import global_config
from hera.workflows import Parameter, RunnerScriptConstructor, script

global_config.experimental_features["script_annotations"] = True


class Input(BaseModel):
    a: int
    b: str = "foo"


class Output(BaseModel):
    output: List[Input]


class InputV1(V1BaseModel):
    a: int
    b: str = "foo"


class OutputV1(V1BaseModel):
    output: List[InputV1]


@script()
def annotated_basic_types(
    a_but_kebab: Annotated[int, Parameter(name="a-but-kebab")] = 2,
    b_but_kebab: Annotated[str, Parameter(name="b-but-kebab")] = "foo",
) -> Output:
    return Output(output=[Input(a=a_but_kebab, b=b_but_kebab)])


@script()
def annotated_basic_types_with_other_metadata(
    a_but_kebab: Annotated[int, "Should skip this one", Parameter(name="a-but-kebab")] = 2,
    b_but_kebab: Annotated[str, "should", "skip", Parameter(name="b-but-kebab"), "this", "one"] = "foo",
) -> Output:
    return Output(output=[Input(a=a_but_kebab, b=b_but_kebab)])

@script()
def annotated_object(annotated_input_value: Annotated[Input, Parameter(name="input-value")]) -> Output:
    return Output(output=[annotated_input_value])


@script(constructor=RunnerScriptConstructor(pydantic_mode=1))
def annotated_object_v1(annotated_input_value: Annotated[InputV1, Parameter(name="input-value")]) -> OutputV1:
    return OutputV1(output=[annotated_input_value])


@script()
def annotated_parameter_no_name(
    annotated_input_value: Annotated[Input, Parameter(description="a value to input")],
) -> Output:
    return Output(output=[annotated_input_value])


@script()
def no_type_parameter(my_anything) -> Any:
    """`my_anything` will be whatever the json loader gives back."""
    return my_anything


@script()
def str_parameter_expects_jsonstr_dict(my_json_str: str) -> dict:
    return json.loads(my_json_str)


@script()
def str_parameter_expects_jsonstr_list(my_json_str: str) -> list:
    return json.loads(my_json_str)


@script()
def annotated_str_parameter_expects_jsonstr_dict(my_json_str: Annotated[str, "some metadata"]) -> list:
    return json.loads(my_json_str)
