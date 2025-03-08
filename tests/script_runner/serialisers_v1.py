import json

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated

from pydantic import BaseModel

from hera.workflows import Parameter, script
from hera.workflows.io.v1 import Input

try:
    from pydantic.v1 import BaseModel
except ImportError:
    from pydantic import BaseModel


class MyParameter(BaseModel):
    a: str = "a"
    b: str = "b"


@script(constructor="runner")
def base_model_auto_load(
    a_parameter: Annotated[MyParameter, Parameter(name="my-parameter")],
) -> str:
    return a_parameter.a + a_parameter.b


class NonUserNonBaseModelClass:
    """Represents a non-user-defined class (e.g. pandas DataFrame) that does not inherit from BaseModel."""

    def __init__(self, a: str, b: str):
        self.a = a
        self.b = b

    @classmethod
    def from_json(cls, json_str) -> "NonUserNonBaseModelClass":
        return cls(**json.loads(json_str))


@script(constructor="runner")
def non_base_model_with_class_loader(
    a_parameter: Annotated[
        NonUserNonBaseModelClass,
        Parameter(name="my-parameter", loader=NonUserNonBaseModelClass.from_json),
    ],
) -> str:
    return a_parameter.a + a_parameter.b


@script(constructor="runner")
def non_base_model_with_lambda_function_loader(
    a_parameter: Annotated[
        NonUserNonBaseModelClass,
        Parameter(name="my-parameter", loader=lambda json_str: NonUserNonBaseModelClass(**json.loads(json_str))),
    ],
) -> str:
    return a_parameter.a + a_parameter.b


# TODO: Also test using Pydantic V2
class MyInput(Input):
    non_user_defined_class: Annotated[
        NonUserNonBaseModelClass, Parameter(name="my-parameter", loader=NonUserNonBaseModelClass.from_json)
    ]


@script(constructor="runner")
def pydantic_input_with_loader_on_attribute(
    my_input: MyInput,
) -> str:
    return my_input.non_user_defined_class.a + my_input.non_user_defined_class.b
