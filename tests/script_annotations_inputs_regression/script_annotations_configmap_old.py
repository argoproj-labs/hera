"""Regression test: compare the new Annotated style inputs declaration with the old version."""

from hera.workflows import (
    Parameter,
    Workflow,
    models as m,
    script,
)


@script(
    inputs=[
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
    ]
)
def echo(message):
    print(message)


with Workflow(
    generate_name="callable-steps-",
    entrypoint="calling-steps",
) as w:
    echo()
