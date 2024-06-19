from typing_extensions import Annotated

from hera.shared import global_config
from hera.workflows import Artifact, ArtifactLoader, Input, Output, WorkflowTemplate

global_config.experimental_features["decorator_syntax"] = True

w = WorkflowTemplate(name="my-template")


class PassthroughIO(Input, Output):
    my_str: str
    my_int: int
    my_artifact: Annotated[str, Artifact(name="my-artifact", loader=ArtifactLoader.json)]


@w.script()
def give_output() -> PassthroughIO:
    return PassthroughIO(my_str="test", my_int=42)


@w.script()
def take_input(inputs: PassthroughIO) -> Output:
    return Output(result=f"Got a string: {inputs.my_str}, got an int: {inputs.my_int}")


@w.dag()
def my_dag():
    output_task = give_output()
    take_input(output_task)
