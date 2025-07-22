from hera.workflows import Script, Step, Steps, Workflow
from hera.workflows.models import Outputs, Parameter, ValueFrom

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    annotations={
        "workflows.argoproj.io/description": "Conditional parameters provide a way to choose the output parameters based on expression.\n\nIn this example the step template has two steps which will run conditionally on `when`.\n\nBased on that condition, one of step will not be executed. The step template's output parameter will be\nset from the executed step's output.\n",
        "workflows.argoproj.io/version": ">= 3.1.0",
    },
    generate_name="conditional-parameter-",
    labels={"workflows.argoproj.io/test": "true"},
    entrypoint="main",
) as w:
    with Steps(
        name="main",
        outputs=Outputs(
            parameters=[
                Parameter(
                    name="stepresult",
                    value_from=ValueFrom(
                        expression="steps['flip-coin'].outputs.result == 'heads' ? steps.heads.outputs.result : steps.tails.outputs.result",
                    ),
                )
            ],
        ),
    ) as invocator:
        Step(
            name="flip-coin",
            template="flip-coin",
        )
        with invocator.parallel():
            Step(
                name="heads",
                template="heads",
                when="{{steps.flip-coin.outputs.result}} == heads",
            )
            Step(
                name="tails",
                template="tails",
                when="{{steps.flip-coin.outputs.result}} == tails",
            )
    Script(
        name="flip-coin",
        command=["python"],
        image="python:alpine3.6",
        source='import random\nprint("heads" if random.randint(0,1) == 0 else "tails")\n',
    )
    Script(
        name="heads",
        command=["python"],
        image="python:alpine3.6",
        source='print("heads")\n',
    )
    Script(
        name="tails",
        command=["python"],
        image="python:alpine3.6",
        source='print("tails")\n',
    )
