from hera.workflows.models import Arguments, Parameter
from hera.workflows.v5.container import Container
from hera.workflows.v5.dag import DAG
from hera.workflows.v5.workflow import Workflow

with Workflow(
    generate_name="dag-diamond-coinflip-",
    annotations={
        "workflows.argoproj.io/description": "This is an example of coin flip defined as a DAG.",
    },
    entrypoint="diamond",
) as w:
    echo = Container(
        name="echo",
        image="alpine:3.7",
        command=["echo", "{{inputs.parameters.message}}"],
        inputs=[Parameter(name="message")],
    )
    with DAG(name="diamond"):
        A = echo(name="A", arguments=Arguments(parameters=[Parameter(name="message", value="A")]))
        B = echo(name="B", arguments=Arguments(parameters=[Parameter(name="message", value="B")]))
        C = echo(name="C", arguments=Arguments(parameters=[Parameter(name="message", value="C")]))
        D = echo(name="D", arguments=Arguments(parameters=[Parameter(name="message", value="D")]))
        A >> [B, C] >> D

w.create()
