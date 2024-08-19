from hera.workflows import Container, Step, Steps, Workflow
from hera.workflows.models import Outputs, Parameter, SuppliedValueFrom, SuspendTemplate, Template, ValueFrom

with Workflow(
    name="suspend-outputs",
    entrypoint="suspend",
) as w:
    print_message = Container(
        name="print-message",
        image="busybox",
        command=["echo"],
        inputs=[Parameter(name="message")],
        args=["{{inputs.parameters.message}}"],
    )

    with Steps(name="suspend"):
        Step(
            name="approve",
            template=Template(
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
            ),
        )
        print_message(name="release", arguments={"message": "{{steps.approve.outputs.parameters.message}}"})
