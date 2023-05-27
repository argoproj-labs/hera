from hera.workflows import DAG, Container, Parameter, Workflow

with Workflow(
    generate_name="loops-dag-",
    entrypoint="loops-dag",
) as w:
    echo = Container(
        name="whalesay",
        image="docker/whalesay:latest",
        command=["cowsay"],
        args=["{{inputs.parameters.message}}"],
        inputs=[Parameter(name="message")],
    )
    with DAG(name="loops-dag"):
        A = echo(name="A", message="A")
        B = echo(name="B", message="{{item}}", with_items=["foo", "bar", "baz"])
        C = echo(name="C", message="C")
        A >> B >> C
