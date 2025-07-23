from hera.workflows import Script, Step, Steps, Workflow
from hera.workflows.models import Arguments, Inputs, Parameter

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    generate_name="recursive-loop-",
    entrypoint="plan",
) as w:
    with Steps(
        name="plan",
    ) as invocator:
        Step(
            arguments=Arguments(
                parameters=[
                    Parameter(
                        name="counter",
                        value="0",
                    ),
                    Parameter(
                        name="limit",
                        value="10",
                    ),
                ],
            ),
            name="recurse",
            template="loop",
        )
    with Steps(
        inputs=Inputs(
            parameters=[
                Parameter(
                    name="counter",
                ),
                Parameter(
                    name="limit",
                ),
            ],
        ),
        name="loop",
    ) as invocator:
        Step(
            arguments=Arguments(
                parameters=[
                    Parameter(
                        name="counter",
                        value="{{inputs.parameters.counter}}",
                    )
                ],
            ),
            name="iterate-counter",
            template="counter-iteration",
        )
        Step(
            arguments=Arguments(
                parameters=[
                    Parameter(
                        name="counter",
                        value="{{steps.iterate-counter.outputs.result}}",
                    ),
                    Parameter(
                        name="limit",
                        value="{{inputs.parameters.limit}}",
                    ),
                ],
            ),
            name="continue",
            template="loop",
            when="{{steps.iterate-counter.outputs.result}} < {{inputs.parameters.limit}}",
        )
    Script(
        inputs=Inputs(
            parameters=[
                Parameter(
                    name="counter",
                )
            ],
        ),
        name="counter-iteration",
        command=["python"],
        image="python:alpine3.6",
        source="print({{inputs.parameters.counter}} + 1)\n",
    )
