from hera.workflows import Container, Step, Steps, Suspend, Workflow
from hera.workflows.models import ValueFrom, SuppliedValueFrom, SuspendTemplate, Template, Parameter, Outputs

with Workflow(
    name="suspend-outputs",
    entrypoint="suspend",
) as w:
    whalesay = Container(
        name="whalesay",
        image="docker/whalesay",
        command=["cowsay"],
        inputs=[Parameter(name="message")],
        args=["{{inputs.parameters.message}}"],
    )

    w._add_sub(
        Template(
            name="approve",
            suspend=SuspendTemplate(),
            outputs=Outputs(
                parameters=[
                    Parameter(
                        name="message",
                        value_from=ValueFrom(supplied=SuppliedValueFrom()),
                    )
                ]
            ),
        )
    )

    with Steps(name="suspend"):
        Step(name="approve", template="approve")
        whalesay(name="release", arguments={"message": "{{steps.approve.outputs.parameters.message}}"})
