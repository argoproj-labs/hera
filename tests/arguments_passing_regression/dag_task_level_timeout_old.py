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
    )
    with DAG(name="diamond"):
        a = echo(name="A", arguments={"timeout": "20s"})
        b = echo(name="B", arguments={"timeout": "10s"})
        c = echo(name="C", arguments={"timeout": "20s"})
        a >> [b, c]
