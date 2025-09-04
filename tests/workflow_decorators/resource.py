from typing_extensions import Annotated

from hera.shared import global_config
from hera.workflows import Input, Output, Parameter, WorkflowTemplate

global_config.experimental_features["script_annotations"] = True
global_config.experimental_features["script_pydantic_io"] = True
global_config.experimental_features["decorator_syntax"] = True


# We start by defining our Workflow Template
w = WorkflowTemplate(name="my-template")


# This defines the template's inputs
class MyResourceInput(Input):
    pvc_size: int


class MyResourceOutput(Output):
    pvc_name: Annotated[
        str,
        Parameter(
            name="pvc-name",
            value_from={"jsonPath": "{.metadata.name}"},
        ),
    ]


@w.set_entrypoint
@w.resource(
    action="create",
    set_owner_reference=True,
    manifest="""apiVersion: v1
kind: PersistentVolumeClaim
metadata:
    generateName: pvc-example-
spec:
    accessModes: ['ReadWriteOnce', 'ReadOnlyMany']
    resources:
    requests:
        storage: '{{inputs.parameters.pvc-size}}'
""",
)
def create_my_pvc_resource(my_input: MyResourceInput) -> MyResourceOutput: ...
