from hera.workflows.models import Parameter
from hera.workflows.v5.container import Container
from hera.workflows.v5.steps import ParallelSteps, Step, Steps
from hera.workflows.v5.workflow import Workflow

whalesay = Container(
    name="whalesay",
    inputs=[Parameter(name="message")],
    image="docker/whalesay",
    command=["cowsay"],
    args=["{{inputs.parameters.message}}"],
)

with Workflow(
    generate_name="steps-",
    entrypoint="hello-hello-hello",
) as w:
    with Steps(name="hello-hello-hello"):
        Step(
            name="hello1",
            template="whalesay",
            arguments=[Parameter(name="message", value="hello1")],
        )

        with ParallelSteps():
            Step(
                name="hello2a",
                template="whalesay",
                arguments=[Parameter(name="message", value="hello2a")],
            )
            Step(
                name="hello2b",
                template="whalesay",
                arguments=[Parameter(name="message", value="hello2b")],
            )

    w.templates.append(whalesay)
