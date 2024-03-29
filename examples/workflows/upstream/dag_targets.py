from hera.workflows import DAG, Container, Parameter, Workflow

with Workflow(
    generate_name="dag-target-",
    entrypoint="dag-target",
    arguments=Parameter(name="target", value="E"),
) as w:
    echo = Container(
        name="echo",
        inputs=Parameter(name="message"),
        image="alpine:3.7",
        command=["echo", "{{inputs.parameters.message}}"],
    )

    with DAG(
        name="dag-target",
        target="{{workflow.parameters.target}}",
    ):
        A = echo(name="A", arguments={"message": "A"})
        B = echo(name="B", arguments={"message": "B"})
        C = echo(name="C", arguments={"message": "C"})
        D = echo(name="D", arguments={"message": "D"})
        E = echo(name="E", arguments={"message": "E"})

        A >> B >> D
        A >> C >> D
        C >> E
