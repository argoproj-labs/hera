from hera.workflows.models import Arguments, Parameter
from hera.workflows.v5.container import Container
from hera.workflows.v5.dag import DAG
from hera.workflows.v5.suspend import Suspend
from hera.workflows.v5.workflow import Workflow

with Workflow(
    generate_name="dag-linear-suspend-",
    annotations={
        "workflows.argoproj.io/description": "This is an example of a linear DAG with multiple suspend points.",
    },
    entrypoint="linear",
) as w:
    echo = Container(
        name="echo",
        image="alpine:3.7",
        command=["echo", "{{inputs.parameters.message}}"],
        inputs=[Parameter(name="message")],
    )
    wait_5_secs = Suspend(name="wait-5-seconds", duration="5")
    wait_until_approved = Suspend(name="wait-until-approved")

    with DAG(name="linear"):
        (
            echo(name="A", arguments=Arguments(parameters=[Parameter(name="message", value="A")]))
            >> wait_5_secs(name="wait-for-a")
            >> echo(name="B", arguments=Arguments(parameters=[Parameter(name="message", value="B")]))
            >> wait_5_secs(name="wait-for-b")
            >> echo(name="C", arguments=Arguments(parameters=[Parameter(name="message", value="C")]))
            >> wait_until_approved(name="wait-for-c-until-approved")
            >> echo(name="D", arguments=Arguments(parameters=[Parameter(name="message", value="D")]))
        )

w.create()
