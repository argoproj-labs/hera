from hera.workflows import (
    Container,
    Parameter,
    Workflow,
    models as m,
)

with Workflow(
    generate_name="global-parameter-from-configmap-referenced-as-local-variable-",
    entrypoint="print-message",
    arguments=Parameter(
        name="message",
        value_from=m.ValueFrom(config_map_key_ref=m.ConfigMapKeySelector(name="simple-parameters", key="msg")),
    ),
) as w:
    Container(
        name="print-message",
        image="busybox",
        command=["echo"],
        args=["{{inputs.parameters.message}}"],
        inputs=Parameter(name="message"),
    )
