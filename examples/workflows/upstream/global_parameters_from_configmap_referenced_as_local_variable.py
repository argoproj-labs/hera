from hera.workflows import (
    Container,
    Parameter,
    Workflow,
    models as m,
)

with Workflow(
    generate_name="global-parameter-from-configmap-referenced-as-local-variable-",
    entrypoint="whalesay",
    arguments=Parameter(
        name="message",
        value_from=m.ValueFrom(config_map_key_ref=m.ConfigMapKeySelector(name="simple-parameters", key="msg")),
    ),
    service_account_name="argo",
) as w:
    Container(
        name="whalesay",
        image="argoproj/argosay:v2",
        args=["echo", "{{inputs.parameters.message}}"],
        inputs=Parameter(name="message"),
    )
