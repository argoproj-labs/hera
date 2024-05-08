from hera.shared import global_config
from hera.workflows import Input, Output, WorkflowTemplate

global_config.experimental_features["script_annotations"] = True
global_config.experimental_features["script_pydantic_io"] = True

w = WorkflowTemplate(name="my-template")


class MyInput(Input):
    user: str


@w.set_entrypoint
@w.script()
def hello_world(my_input: MyInput) -> Output:
    output = Output()
    output.result = f"Hello Hera User: {my_input.user}!"
    return output


@w.set_entrypoint
@w.script()
def hello_world_2(my_input: MyInput) -> Output:
    output = Output()
    output.result = f"Hello Hera User: {my_input.user}!"
    return output
