"""Regression test: compare the new Annotated style inputs declaration with the old version."""

from typing import Annotated

from hera.shared import global_config
from hera.workflows import Workflow, script
from hera.workflows.parameter import Parameter
from hera.workflows.steps import Steps

global_config.experimental_features["script_annotations"] = True


@script()
def echo_all(
    an_int: Annotated[int, Parameter(description="an_int parameter", enum=[1, 2, 3])] = 1,
    a_bool: Annotated[bool, Parameter(description="a_bool parameter", enum=[True, False])] = True,
    a_string: Annotated[str, Parameter(description="a_string parameter", enum=["a", "b", "c"])] = "a",
):
    print(an_int)
    print(a_bool)
    print(a_string)


with Workflow(generate_name="test-artifacts-", entrypoint="my-steps") as w:
    with Steps(name="my-steps") as s:
        echo_all(arguments={"an_int": 1, "a_bool": True, "a_string": "a"})
