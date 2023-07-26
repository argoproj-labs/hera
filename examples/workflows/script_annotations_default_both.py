try:
    from typing import Annotated  # type: ignore
except ImportError:
    from typing_extensions import Annotated  # type: ignore

from hera.shared import global_config
from hera.workflows import Workflow, script
from hera.workflows.parameter import Parameter
from hera.workflows.steps import Steps

global_config.experimental_features["script_annotations"] = True


@script()
def echo_new(an_int: Annotated[int, Parameter(default=1)]):
    print(an_int)


# note that you can use the Annotated for other fields and the Python default
@script()
def echo_old(an_int: Annotated[int, Parameter(name="another_name")] = 1):
    print(an_int)


with Workflow(generate_name="test-types-", entrypoint="my_steps") as w:
    with Steps(name="my_steps") as s:
        echo_new(arguments={"an_int": 1})
        echo_old(arguments={"an_int": 1})
