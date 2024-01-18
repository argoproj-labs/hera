try:
    from pydantic.v1 import BaseModel
except ImportError:
    from pydantic import BaseModel

from hera.shared import global_config
from hera.workflows import Artifact, ArtifactLoader, Parameter, Workflow, script
from hera.workflows.io import RunnerInput, RunnerOutput

try:
    from typing import Annotated  # type: ignore
except ImportError:
    from typing_extensions import Annotated  # type: ignore

global_config.experimental_features["script_annotations"] = True
global_config.experimental_features["script_pydantic_io"] = True


class MyObject(BaseModel):
    a_dict: dict = {}
    a_str: str = "a default string"


class MyInput(RunnerInput):
    param_int: Annotated[int, Parameter(name="param-input")] = 42
    an_object: Annotated[MyObject, Parameter(name="obj-input")] = MyObject(
        a_dict={"my-key": "a-value"}, a_str="hello world!"
    )
    artifact_int: Annotated[int, Artifact(name="artifact-input", loader=ArtifactLoader.json)]


class MyOutput(RunnerOutput):
    param_int: Annotated[int, Parameter(name="param-output")]
    artifact_int: Annotated[int, Artifact(name="artifact-output")]


@script(constructor="runner")
def pydantic_io(
    my_input: MyInput,
) -> MyOutput:
    return MyOutput(exit_code=1, result="Test!", param_int=42, artifact_int=my_input.param_int)


with Workflow(generate_name="pydantic-io-") as w:
    pydantic_io()
