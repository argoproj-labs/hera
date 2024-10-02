from hera.shared import global_config
from hera.workflows import Input, Output, Workflow

global_config.experimental_features["decorator_syntax"] = True


class ExampleOutput(Output):
    field: str


w = Workflow(generate_name="my-workflow-")


@w.script()
def my_script(_: Input) -> ExampleOutput:
    return ExampleOutput(field="Hello world!")


@w.dag()
def dag(_: Input):
    task = my_script(Input())
    return ExampleOutput(field=task.field)
