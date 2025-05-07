import json
import pickle

from hera.shared import global_config
from hera.workflows import Artifact, ArtifactLoader, script
from hera.workflows.io.v1 import Input, Output

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated
try:
    from pydantic.v1 import BaseModel
except ImportError:
    from pydantic import BaseModel

global_config.experimental_features["script_pydantic_io"] = True


class MyBaseModel(BaseModel):
    a: str = "a"
    b: str = "b"


@script(constructor="runner")
def base_model_auto_load(
    an_artifact: Annotated[MyBaseModel, Artifact(name="my-artifact", loader=ArtifactLoader.json)],
) -> str:
    return an_artifact.a + an_artifact.b


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
    an_artifact: Annotated[
        NonUserNonBaseModelClass,
        Artifact(name="my-artifact", loads=NonUserNonBaseModelClass.from_json),
    ],
) -> str:
    return an_artifact.a + an_artifact.b


@script(constructor="runner")
def bytes_loader(
    an_artifact: Annotated[
        bytes,
        Artifact(name="my-artifact", loadb=lambda b: pickle.loads(b)),
    ],
) -> bytes:
    return an_artifact


@script(constructor="runner")
def non_base_model_with_lambda_function_loader(
    an_artifact: Annotated[
        NonUserNonBaseModelClass,
        Artifact(name="my-artifact", loads=lambda json_str: NonUserNonBaseModelClass(**json.loads(json_str))),
    ],
) -> str:
    return an_artifact.a + an_artifact.b


class MyInput(Input):
    non_user_defined_class: Annotated[
        NonUserNonBaseModelClass, Artifact(name="my-artifact", loads=NonUserNonBaseModelClass.from_json)
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
) -> Annotated[MyBaseModel, Artifact(name="my-output-artifact")]:
    return MyBaseModel(a=a, b=b)


@script(constructor="runner")
def bytes_dumper(
    a: str,
    b: str,
) -> Annotated[bytes, Artifact(name="my-output-artifact", dumpb=lambda x: pickle.dumps(x))]:
    return (a + b).encode("utf-8")


@script(constructor="runner")
def non_base_model_with_class_serialiser(
    a: str,
    b: str,
) -> Annotated[
    NonUserNonBaseModelClass,
    Artifact(name="my-output-artifact", dumps=NonUserNonBaseModelClass.to_json),
]:
    return NonUserNonBaseModelClass(a=a, b=b)


class MyOutput(Output):
    non_user_defined_class: Annotated[
        NonUserNonBaseModelClass, Artifact(name="my-output-artifact", dumps=NonUserNonBaseModelClass.to_json)
    ]


@script(constructor="runner")
def pydantic_output_with_dumper_on_attribute(
    a: str,
    b: str,
) -> MyOutput:
    return MyOutput(non_user_defined_class=NonUserNonBaseModelClass(a=a, b=b))
