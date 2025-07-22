from hera.workflows import Container, Workflow
from hera.workflows.models import Arguments, LabelValueFrom, Parameter, WorkflowMetadata

with Workflow(
    arguments=Arguments(
        parameters=[
            Parameter(
                name="foo",
                value="bar",
            )
        ],
    ),
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    annotations={
        "workflows.argoproj.io/version": ">= v3.3.0",
        "workflows.argoproj.io/description": "This examples show you how to add labels based on an expression.\nYou can then query workflows based on the parameters they were invoked with.\nIn this specific case, the value of foo will set as a label on the workflow.\n",
    },
    generate_name="label-value-from-",
    entrypoint="main",
    workflow_metadata=WorkflowMetadata(
        labels_from={
            "foo": LabelValueFrom(
                expression="workflow.parameters.foo",
            )
        },
    ),
) as w:
    Container(
        name="main",
        image="argoproj/argosay:v2",
    )
