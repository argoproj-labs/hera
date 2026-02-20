from typing import Annotated, List

from hera.workflows import DAG, Input, Output, Parameter, Workflow, script


class GenerateOutput(Output):
    some_values: Annotated[List[int], Parameter(name="some-values")]


class ConsumeInput(Input):
    some_value: Annotated[int, Parameter(name="some-value", description="this is some value")]


@script(constructor="runner")
def generate() -> GenerateOutput:
    return GenerateOutput(some_values=[i for i in range(10)])


@script(constructor="runner")
def consume(input: ConsumeInput) -> None:
    print("Received value: {value}!".format(value=input.some_value))


with Workflow(generate_name="dynamic-fanout-", entrypoint="d") as w:
    with DAG(name="dag"):
        g = generate(arguments={})
        c = consume(with_param=g.get_parameter("some-values"))
        g >> c
