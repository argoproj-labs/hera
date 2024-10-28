from typing import Literal

from hera.workflows import Steps, Workflow, script


@script(constructor="runner")
def literal_str(my_str: Literal["foo", "bar"]) -> Literal[1, 2]:
    return {"foo": 1, "bar": 2}[my_str]


with Workflow(name="my-workflow", entrypoint="steps") as w:
    with Steps(name="steps"):
        literal_str()
