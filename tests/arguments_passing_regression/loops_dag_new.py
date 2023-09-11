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
        use_func_params_in_call=True,
    )
    with DAG(name="loops-dag"):
        A = echo("A").with_(name="A")
        B = echo("{{item}}").with_(name="B", with_items=["foo", "bar", "baz"])
        C = echo("C").with_(name="C")
        A >> B >> C
