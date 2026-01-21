from hera.workflows import Script, Step, Steps, Workflow
from hera.workflows.models import Arguments, Inputs, IntOrString, Parameter, RetryStrategy

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    generate_name="retry-script-",
    entrypoint="main",
) as w:
    with Steps(
        name="main",
    ) as invocator:
        Step(
            name="safe-to-retry",
            template="safe-to-retry",
        )
        Step(
            arguments=Arguments(
                parameters=[
                    Parameter(
                        name="safe-to-retry",
                        value="{{steps.safe-to-retry.outputs.result}}",
                    )
                ],
            ),
            name="retry",
            template="retry-script",
        )
    Script(
        name="safe-to-retry",
        command=["python"],
        image="python:alpine3.6",
        source='print("true")\n',
    )
    Script(
        inputs=Inputs(
            parameters=[
                Parameter(
                    name="safe-to-retry",
                )
            ],
        ),
        name="retry-script",
        retry_strategy=RetryStrategy(
            expression="""\
asInt(lastRetry.exitCode) > 1 && \
lastRetry.status != "Error" && \
asInt(lastRetry.duration) < 120 && \
({{inputs.parameters.safe-to-retry}} == true || lastRetry.message matches 'imminent node shutdown|pod deleted')""",
            limit=IntOrString(
                root="10",
            ),
        ),
        command=["python"],
        image="python:alpine3.6",
        source="import random;\nimport sys;\nexit_code = random.choice([1, 2]);\nsys.exit(exit_code)\n",
    )
