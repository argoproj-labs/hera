from hera.workflows import (
    Parameter,
    Resource,
    Step,
    Steps,
    Workflow,
    models as m,
)

with Workflow(
    generate_name="resource-delete-with-flags-",
    entrypoint="main",
) as w:
    create_configmap = Resource(
        name="create-configmap",
        action="create",
        manifest="""apiVersion: v1
kind: ConfigMap
metadata:
  name: resource-delete-with-flags
  labels:
    cleanup: "true"
data:
  key: value
""",
    )

    delete_resource = Resource(
        name="delete-resource",
        action="delete",
        flags=["configmap", "--selector", "{{inputs.parameters.selector}}"],
        inputs=m.Inputs(
            parameters=[Parameter(name="selector")],
        ),
    )

    with Steps(name="main") as s:
        Step(name="submit-resource", template=create_configmap.name)
        Step(
            name="delete-resource",
            template=delete_resource.name,
            arguments=[
                Parameter(name="selector", value="cleanup=true"),
            ],
        )
