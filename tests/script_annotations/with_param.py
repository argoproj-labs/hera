from typing import Annotated, List

from hera.shared import global_config
from hera.workflows import DAG, Parameter, Workflow, script

global_config.experimental_features["script_annotations"] = True


@script(constructor="runner")
def generate() -> Annotated[List[int], Parameter(name="some-values")]:
    return [i for i in range(10)]


@script(constructor="runner")
def consume(some_value: Annotated[int, Parameter(name="some-value", description="this is some value")]):
    print("Received value: {value}!".format(value=some_value))


with Workflow(generate_name="dynamic-fanout-", entrypoint="d") as w:
    with DAG(name="dag"):
        g = generate(arguments={})
        c = consume(with_param=g.get_parameter("some-values"))
        g >> c
