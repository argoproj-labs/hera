import json
from typing import Any, List

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated

from pydantic import BaseModel

from hera.shared import global_config
from hera.workflows import Parameter, script

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
def annotated_parameter_no_name(
    annotated_input_value: Annotated[Input, Parameter(description="a value to input")]
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


class MyStr(str):
    pass


@script()
def str_subclass_parameter_expects_jsonstr_dict(my_json_str: MyStr) -> list:
    return json.loads(my_json_str)


@script()
def str_subclass_annotated_parameter_expects_jsonstr_dict(my_json_str: Annotated[MyStr, "some metadata"]) -> list:
    return json.loads(my_json_str)
