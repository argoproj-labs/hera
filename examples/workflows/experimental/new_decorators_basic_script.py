from hera.shared import global_config
from hera.workflows import RunnerInput, RunnerOutput, WorkflowTemplate

global_config.experimental_features["script_annotations"] = True
global_config.experimental_features["script_pydantic_io"] = True

w = WorkflowTemplate(name="my-template")


class MyInput(RunnerInput):
    user: str


@w.set_entrypoint()
@w.script()
def hello_world(my_input: MyInput) -> RunnerOutput:
    output = RunnerOutput()
    output.result = f"Hello Hera User: {my_input.user}!"
    return output
