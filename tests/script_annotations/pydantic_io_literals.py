from typing import Literal

from hera.workflows import Input, Output, Steps, Workflow, script


class ExampleInput(Input):
    my_str: Literal["foo", "bar"]


class ExampleOutput(Output):
    index: Literal[1, 2]


@script(constructor="runner")
def literal_str(input: ExampleInput) -> ExampleOutput:
    return ExampleOutput(index={"foo": 1, "bar": 2}[input.my_str])


with Workflow(name="my-workflow", entrypoint="steps") as w:
    with Steps(name="steps"):
        literal_str()
