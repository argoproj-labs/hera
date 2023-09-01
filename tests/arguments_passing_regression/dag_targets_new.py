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
        directly_callable=True,
    )

    with DAG(
        name="dag-target",
        target="{{workflow.parameters.target}}",
    ):
        A = echo("A").with_(name="A")
        B = echo("B").with_(name="B")
        C = echo("C").with_(name="C")
        D = echo("D").with_(name="D")
        E = echo("E").with_(name="E")

        A >> B >> D
        A >> C >> D
        C >> E
