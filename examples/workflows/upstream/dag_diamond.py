from hera.workflows import DAG, Container, Parameter, Workflow

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
        A = echo(name="A", message="A")
        B = echo(name="B", message="B")
        C = echo(name="C", message="C")
        D = echo(name="D", message="D")
        A >> [B, C] >> D
