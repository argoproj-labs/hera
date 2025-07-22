from hera.workflows import Container, Script, Step, Steps, Workflow
from hera.workflows.models import Arguments, Inputs, Parameter

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    generate_name="scripts-javascript-",
    entrypoint="javascript-script-example",
) as w:
    with Steps(
        name="javascript-script-example",
    ) as invocator:
        Step(
            name="generate",
            template="gen-random-int",
        )
        Step(
            arguments=Arguments(
                parameters=[
                    Parameter(
                        name="message",
                        value="{{steps.generate.outputs.result}}",
                    )
                ],
            ),
            name="print",
            template="print-message",
        )
    Script(
        name="gen-random-int",
        command=["node"],
        image="node:9.1-alpine",
        source="var rand = Math.floor(Math.random() * 100);\nconsole.log(rand);\n",
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
        args=["echo result was: {{inputs.parameters.message}}"],
        command=["sh", "-c"],
        image="alpine:latest",
    )
