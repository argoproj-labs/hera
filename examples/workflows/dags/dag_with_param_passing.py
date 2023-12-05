from hera.workflows import DAG, Container, Parameter, Task, Workflow

with Workflow(generate_name="param-passing-", entrypoint="d") as w:
    out = Container(
        name="out",
        image="docker/whalesay:latest",
        command=["cowsay"],
        outputs=Parameter(name="x", value=42),
    )
    in_ = Container(
        name="in",
        image="docker/whalesay:latest",
        command=["cowsay"],
        args=["{{inputs.parameters.a}}"],
        inputs=Parameter(name="a"),
    )
    with DAG(name="d"):
        t1 = Task(name="a", template=out)
        t2 = Task(name="b", template=in_, arguments=t1.get_parameter("x").with_name("a"))
        t1 >> t2
