from hera.workflows import DAG, Container, Parameter, Workflow

with Workflow(
    generate_name="dag-task-level-timeout-",
    entrypoint="diamond",
) as w:
    echo = Container(
        name="echo",
        timeout="{{inputs.parameters.timeout}}",
        image="alpine:3.7",
        command=["sleep", "15s"],
        inputs=Parameter(name="timeout"),
        use_func_params_in_call=True,
    )
    with DAG(name="diamond"):
        a = echo("20s").with_(name="A")
        b = echo("10s").with_(name="B")
        c = echo("20s").with_(name="C")
        a >> [b, c]
