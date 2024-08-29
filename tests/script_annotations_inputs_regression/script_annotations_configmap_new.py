"""Regression test: compare the new Annotated style inputs declaration with the old version."""

import sys

if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated

from hera.workflows import (
    Parameter,
    Workflow,
    models as m,
    script,
)


@script()
def echo(
    message: Annotated[
        str,
        Parameter(
            name="message",
            value_from=m.ValueFrom(
                config_map_key_ref=m.ConfigMapKeySelector(
                    name="simple-parameters",
                    key="msg",
                ),
                default="configmap-default",
                event="configmap-event",
                expression="configmap-expression",
                jq_filter="configmap-jq_filter",
                json_path="configmap-json_path",
                parameter="configmap-parameter",
                path="configmap-path",
                supplied={"name": "configmap-supplied"},
            ),
        ),
    ],
):
    print(message)


with Workflow(
    generate_name="callable-steps-",
    entrypoint="calling-steps",
) as w:
    echo()
