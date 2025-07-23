from hera.workflows import Container, Step, Steps, Workflow
from hera.workflows.models import Arguments, ContinueOn, Inputs, Parameter

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    generate_name="exit-code-output-variable-",
    entrypoint="exit-code-output-variable",
) as w:
    with Steps(
        name="exit-code-output-variable",
    ) as invocator:
        Step(
            name="failing-container",
            continue_on=ContinueOn(
                failed=True,
            ),
            template="failing-container",
        )
        Step(
            arguments=Arguments(
                parameters=[
                    Parameter(
                        name="exitCode",
                        value="{{steps.failing-container.exitCode}}",
                    )
                ],
            ),
            name="echo-container",
            template="echo-container",
        )
    Container(
        name="failing-container",
        args=["exit 123"],
        command=["sh", "-c"],
        image="alpine:3.6",
    )
    Container(
        inputs=Inputs(
            parameters=[
                Parameter(
                    name="exitCode",
                )
            ],
        ),
        name="echo-container",
        args=['echo "Exit code was: {{inputs.parameters.exitCode}}"'],
        command=["sh", "-c"],
        image="alpine:3.6",
    )
