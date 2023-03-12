from hera.workflows import (
    DAG,
    Container,
    Parameter,
    Task,
    Workflow,
    models as m,
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
        A = Task(name="A", template=echo, arguments=m.Arguments(parameters=[Parameter(name="message", value="A")]))
        B = Task(name="B", template=echo, arguments=m.Arguments(parameters=[Parameter(name="message", value="B")]))
        C = Task(name="C", template=echo, arguments=m.Arguments(parameters=[Parameter(name="message", value="C")]))
        D = Task(name="D", template=echo, arguments=m.Arguments(parameters=[Parameter(name="message", value="D")]))
        A >> [B, C] >> D
