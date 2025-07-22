from hera.workflows import Container, Script, Step, Steps, Workflow
from hera.workflows.models import Arguments, Inputs, Parameter

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    generate_name="scripts-bash-",
    entrypoint="bash-script-example",
) as w:
    with Steps(
        name="bash-script-example",
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
        command=["bash"],
        image="debian:9.4",
        source="cat /dev/urandom | od -N2 -An -i | awk -v f=1 -v r=100 '{printf \"%i\\n\", f + r * $1 / 65536}'\n",
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
