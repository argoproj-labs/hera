from hera.workflows import (
    Container,
    Parameter,
    Workflow,
    models as m,
)

with Workflow(
    generate_name="arguments-parameters-from-configmap-",
    entrypoint="print-message-from-configmap",
) as w:
    Container(
        name="print-message-from-configmap",
        image="busybox",
        command=["echo"],
        args=["{{inputs.parameters.message}}"],
        inputs=Parameter(
            name="message",
            value_from=m.ValueFrom(
                config_map_key_ref=m.ConfigMapKeySelector(
                    name="simple-parameters",
                    key="msg",
                )
            ),
        ),
    )
