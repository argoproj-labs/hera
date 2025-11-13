"""This example shows the use of Pydantic Input/Output to create the input and output parameters and artifacts for a script template."""

from typing import Annotated

from pydantic.v1 import BaseModel

from hera.shared import global_config
from hera.workflows import Artifact, ArtifactLoader, Parameter, Script, Steps, Workflow, script
from hera.workflows.archive import NoneArchiveStrategy
from hera.workflows.io import Input, Output

global_config.experimental_features["script_pydantic_io"] = True
global_config.set_class_defaults(Script, constructor="runner")
global_config.set_class_defaults(Script, image="my-image-with-deps")


class MyObject(BaseModel):
    a_dict: dict  # not giving a default makes the field a required input for the template
    a_str: str = "a default string"


class MyInput(Input):
    param_int: Annotated[int, Parameter(name="param-input")] = 42
    an_object: Annotated[MyObject, Parameter(name="obj-input")] = MyObject(
        a_dict={"my-key": "a-value"}, a_str="hello world!"
    )
    artifact_int: Annotated[int, Artifact(name="artifact-input", loader=ArtifactLoader.json)]


class MyOutput(Output):
    param_int: Annotated[int, Parameter(name="param-output")]
    artifact_int: Annotated[int, Artifact(name="artifact-output")]


@script()
def writer() -> Annotated[int, Artifact(name="int-artifact", archive=NoneArchiveStrategy())]:
    return 100


@script()
def pydantic_io(
    my_input: MyInput,
) -> MyOutput:
    return MyOutput(exit_code=1, result="Test!", param_int=42, artifact_int=my_input.param_int)


with Workflow(generate_name="pydantic-io-", entrypoint="use-pydantic-io") as w:
    with Steps(name="use-pydantic-io"):
        write_step = writer()
        pydantic_io(
            arguments=[
                write_step.get_artifact("int-artifact").with_name("artifact-input"),
                {
                    "param_int": 101,
                    "an_object": MyObject(a_dict={"my-new-key": "my-new-value"}),
                },
            ]
        )
