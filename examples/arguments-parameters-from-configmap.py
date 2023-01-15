"""This example showcases how to set arguments and parameters from a configmap.

https://github.com/argoproj/argo-workflows/blob/master/examples/arguments-parameters-from-configmap.yaml
"""

from hera import (
    ConfigMapKeySelector,
    Container,
    Parameter,
    Task,
    ValueFrom,
    Workflow,
    WorkflowMetadata,
)

with Workflow(
    generate_name="arguments-parameters-from-configmap-",
    workflow_metadata=WorkflowMetadata(
        labels={
            "workflows.argoproj.io/test": "true",
        },
        annotations={
            "workflows.argoproj.io/description": "This example demonstrates loading parameter values from configmap. "
            "Note that the `simple-parameters` ConfigMap "
            "(defined in examples/configmaps/simple-parameters-configmap.yaml) needs "
            "to be created first before submitting this workflow.",
            "workflows.argoproj.io/verify.": 'assert status["phase"] == "Succeeded"',
        },
    ),
    service_account_name="argo",
) as w:
    Task(
        "whalesay",
        inputs=[
            Parameter(
                name="message",
                value_from=ValueFrom(config_map_key_ref=ConfigMapKeySelector(key="msg", name="single-parameters")),
            )
        ],
        container=Container(image="argoproj/argosay:v2"),
        args=["echo", "{{inputs.parameters.message}}"],
    )


w.create()
