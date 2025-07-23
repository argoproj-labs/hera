from hera.workflows import Container, Step, Steps, Workflow
from hera.workflows.models import Arguments, ContinueOn, Inputs, Parameter

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    generate_name="steps-tmpl-timeout-",
    entrypoint="sleep-sleep",
) as w:
    with Steps(
        name="sleep-sleep",
    ) as invocator:
        with invocator.parallel():
            Step(
                arguments=Arguments(
                    parameters=[
                        Parameter(
                            name="timeout",
                            value="10s",
                        )
                    ],
                ),
                name="sleep1",
                continue_on=ContinueOn(
                    error=True,
                ),
                template="sleep",
            )
            Step(
                arguments=Arguments(
                    parameters=[
                        Parameter(
                            name="timeout",
                            value="10s",
                        )
                    ],
                ),
                name="sleep2",
                continue_on=ContinueOn(
                    failed=True,
                ),
                template="sleep",
            )
    Container(
        inputs=Inputs(
            parameters=[
                Parameter(
                    name="timeout",
                )
            ],
        ),
        name="sleep",
        timeout="{{inputs.parameters.timeout}}",
        args=["sleep 30s"],
        command=["sh", "-c"],
        image="alpine:latest",
    )
