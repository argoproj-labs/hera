"""
This example showcases how clients can use Hera to dynamically generate tasks that process outputs from one task in
parallel. This is useful for batch jobs and instances where clients do not know ahead of time how many tasks/entities
they may need to process.
"""

from typing import Annotated, List

from hera.shared import global_config
from hera.workflows import DAG, Input, Output, Parameter, Workflow, script

global_config.experimental_features["script_pydantic_io"] = True


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


# assumes you used `hera.set_global_token` and `hera.set_global_host` so that the workflow can be submitted
with Workflow(generate_name="dynamic-fanout-", entrypoint="d") as w:
    with DAG(name="d"):
        g = generate(arguments={})
        c = consume(with_param=g.get_parameter("some-values"))
        g >> c
