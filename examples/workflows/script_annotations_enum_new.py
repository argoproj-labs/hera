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
def echo_int(an_int: Annotated[int, Parameter(enum=[1, 2, 3])]):
    print(an_int)


@script()
def echo_boolean(a_bool: Annotated[bool, Parameter(enum=[True])]):
    print(a_bool)


@script()
def echo_string(a_string: Annotated[str, Parameter(enum=["a", "b", "c"])]):
    print(a_string)


with Workflow(generate_name="test-types-", entrypoint="my_steps") as w:
    with Steps(name="my_steps") as s:
        echo_int(arguments={"an_int": 1})
        echo_boolean(arguments={"a_bool": True})
        echo_string(arguments={"a_string": "a"})
