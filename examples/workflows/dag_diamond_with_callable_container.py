from hera.workflows import (
    DAG,
    Container,
    Parameter,
    Workflow,
)

with Workflow(
    generate_name="dag-diamond-",
    entrypoint="diamond",
) as w:
    echo = Container(
        name="echo",
        image="alpine:3.7",
        command=["echo", "{{inputs.parameters.message}}"],
        inputs=[Parameter(name="message")],
    )
    with DAG(name="diamond"):
        A = echo(name="A", arguments=[Parameter(name="message", value="A")])
        B = echo(name="B", arguments=[Parameter(name="message", value="B")])
        C = echo(name="C", arguments=[Parameter(name="message", value="C")])
        D = echo(name="D", arguments=[Parameter(name="message", value="D")])
        A >> [B, C] >> D
