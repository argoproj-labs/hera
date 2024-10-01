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
def dag(_: Input) -> ExampleOutput:
    # example_output is actually a Task when running the DAG decorator logic
    example_output = my_script(Input())
    return example_output
