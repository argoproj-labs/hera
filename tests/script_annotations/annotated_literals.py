from typing import Annotated, Literal

from hera.shared import global_config
from hera.workflows import Parameter, Steps, Workflow, script

global_config.experimental_features["script_annotations"] = True


@script(constructor="runner")
def literal_str(
    my_str: Annotated[Literal["foo", "bar"], Parameter(name="my-str")],
) -> Annotated[Literal[1, 2], Parameter(name="index")]:
    return {"foo": 1, "bar": 2}[my_str]


with Workflow(name="my-workflow", entrypoint="steps") as w:
    with Steps(name="steps"):
        literal_str()
