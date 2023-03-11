from hera.workflows.models import Arguments, Inputs, Parameter
from hera.workflows.v5.resource import Resource
from hera.workflows.v5.steps import Step, Steps
from hera.workflows.v5.workflow import Workflow

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
    flags=[
        "configmap", "--selector", "{{inputs.parameters.selector}}"
    ],
    inputs=Inputs(
        parameters=[Parameter(name="selector")],
    )
)

with Workflow(
    generate_name="resource-delete-with-flags-",
    templates=[create_configmap, delete_resource],
    entrypoint="main",
) as w:
    with Steps(name="main") as s:
        Step(name="submit-resource", template=create_configmap.name)
        Step(
            name="delete-resource",
            template=delete_resource.name,
            arguments=[
                Parameter(name="selector", value="cleanup=true"),
            ],
        )
