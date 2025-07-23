from hera.workflows import Container, Step, Steps, Workflow
from hera.workflows.models import Arguments, Inputs, Metadata, Parameter

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    generate_name="steps-",
    entrypoint="hello-hello-hello",
    pod_metadata=Metadata(
        annotations={"iam.amazonaws.com/role": "role-arn"},
        labels={"app": "print-message", "tier": "demo"},
    ),
) as w:
    with Steps(
        name="hello-hello-hello",
    ) as invocator:
        Step(
            arguments=Arguments(
                parameters=[
                    Parameter(
                        name="message",
                        value="hello1",
                    )
                ],
            ),
            name="hello1",
            template="print-message",
        )
    Container(
        inputs=Inputs(
            parameters=[
                Parameter(
                    name="message",
                )
            ],
        ),
        name="print-message",
        args=["{{inputs.parameters.message}}"],
        command=["echo"],
        image="busybox",
    )
