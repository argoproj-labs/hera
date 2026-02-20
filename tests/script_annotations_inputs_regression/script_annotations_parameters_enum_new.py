"""Regression test: compare the new Annotated style inputs declaration with the old version."""

from typing import Annotated

from hera.workflows import Workflow, script
from hera.workflows.parameter import Parameter
from hera.workflows.steps import Steps


@script()
def echo_int(an_int: Annotated[int, Parameter(enum=[1, 2, 3])]):
    print(an_int)


@script()
def echo_boolean(a_bool: Annotated[bool, Parameter(enum=[True])]):
    print(a_bool)


@script()
def echo_string(a_string: Annotated[str, Parameter(enum=["a", "b", "c"])]):
    print(a_string)


with Workflow(generate_name="test-artifacts-", entrypoint="my-steps") as w:
    with Steps(name="my-steps") as s:
        echo_int(arguments={"an_int": 1})
        echo_boolean(arguments={"a_bool": True})
        echo_string(arguments={"a_string": "a"})
