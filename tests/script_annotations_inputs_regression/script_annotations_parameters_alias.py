"""Regression test: compare the new Annotated style inputs declaration with the old version."""

import sys

if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated

from hera.shared import global_config
from hera.workflows import Workflow, script
from hera.workflows.parameter import Parameter
from hera.workflows.steps import Steps

global_config.experimental_features["script_annotations"] = True


@script()
def echo(
    a_name: Annotated[str, Parameter(name="another_name")],
):
    print(a_name)


with Workflow(generate_name="test-artifacts-", entrypoint="my-steps") as w:
    with Steps(name="my-steps") as s:
        echo(arguments={"a_name": "hello there"})
