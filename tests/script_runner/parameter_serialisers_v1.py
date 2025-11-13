import json

from pydantic.v1 import BaseModel
from typing_extensions import TypedDict

from hera.shared import global_config
from hera.workflows import Parameter, script
from hera.workflows.io.v1 import Input, Output

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated

global_config.experimental_features["script_pydantic_io"] = True


class MyBaseModel(BaseModel):
    a: str = "a"
    b: str = "b"


@script(constructor="runner")
def base_model_auto_load(
    a_parameter: Annotated[MyBaseModel, Parameter(name="my-parameter")],
) -> str:
    return a_parameter.a + a_parameter.b


class NonTypeCheckableTypedDict(TypedDict):
    a: str
    b: str


@script(constructor="runner")
def load_typed_dict(
    a_parameter: Annotated[
        NonTypeCheckableTypedDict,
        Parameter(name="my-parameter", loads=lambda json_str: NonTypeCheckableTypedDict(**json.loads(json_str))),
    ],
) -> str:
    return a_parameter["a"] + a_parameter["b"]


@script(constructor="runner")
def load_wrong_type(
    a_parameter: Annotated[
        float,
        Parameter(name="my-parameter", loads=lambda _: "hello"),
    ],
) -> str:
    return a_parameter + " world"


class NonUserNonBaseModelClass:
    """Represents a non-user-defined class (e.g. pandas DataFrame) that does not inherit from BaseModel."""

    def __init__(self, a: str, b: str):
        self.a = a
        self.b = b

    @classmethod
    def from_json(cls, json_str) -> "NonUserNonBaseModelClass":
        return cls(**json.loads(json_str))

    def to_json(self) -> str:
        self_dict = {
            "a": self.a,
            "b": self.b,
        }
        return json.dumps(self_dict)


@script(constructor="runner")
def non_base_model_with_class_loader(
    a_parameter: Annotated[
        NonUserNonBaseModelClass,
        Parameter(name="my-parameter", loads=NonUserNonBaseModelClass.from_json),
    ],
) -> str:
    return a_parameter.a + a_parameter.b


@script(constructor="runner")
def non_base_model_with_lambda_function_loader(
    a_parameter: Annotated[
        NonUserNonBaseModelClass,
        Parameter(name="my-parameter", loads=lambda json_str: NonUserNonBaseModelClass(**json.loads(json_str))),
    ],
) -> str:
    return a_parameter.a + a_parameter.b


class MyInput(Input):
    non_user_defined_class: Annotated[
        NonUserNonBaseModelClass, Parameter(name="my-parameter", loads=NonUserNonBaseModelClass.from_json)
    ]


@script(constructor="runner")
def pydantic_input_with_loader_on_attribute(
    my_input: MyInput,
) -> str:
    return my_input.non_user_defined_class.a + my_input.non_user_defined_class.b


@script(constructor="runner")
def base_model_auto_save(
    a: str,
    b: str,
) -> Annotated[MyBaseModel, Parameter(name="my-output")]:
    return MyBaseModel(a=a, b=b)


@script(constructor="runner")
def non_base_model_with_class_serialiser(
    a: str,
    b: str,
) -> Annotated[
    NonUserNonBaseModelClass,
    Parameter(name="my-output", dumps=NonUserNonBaseModelClass.to_json),
]:
    return NonUserNonBaseModelClass(a=a, b=b)


class MyOutput(Output):
    non_user_defined_class: Annotated[
        NonUserNonBaseModelClass, Parameter(name="my-output", dumps=NonUserNonBaseModelClass.to_json)
    ]


@script(constructor="runner")
def pydantic_output_with_dumper_on_attribute(
    a: str,
    b: str,
) -> MyOutput:
    return MyOutput(non_user_defined_class=NonUserNonBaseModelClass(a=a, b=b))
