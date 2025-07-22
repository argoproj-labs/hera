from hera.workflows import DAG, Container, Task, Workflow

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    generate_name="dag-contiue-on-fail-",
    entrypoint="workflow",
) as w:
    with DAG(
        name="workflow",
    ) as invocator:
        Task(
            name="A",
            template="hello-world",
        )
        Task(
            name="B",
            template="intentional-fail",
            depends="A",
        )
        Task(
            name="C",
            template="hello-world",
            depends="A",
        )
        Task(
            name="D",
            template="hello-world",
            depends="B.Failed && C",
        )
        Task(
            name="E",
            template="intentional-fail",
            depends="A",
        )
        Task(
            name="F",
            template="hello-world",
            depends="A",
        )
        Task(
            name="G",
            template="hello-world",
            depends="E && F",
        )
    Container(
        name="hello-world",
        args=["hello world"],
        command=["echo"],
        image="busybox",
    )
    Container(
        name="intentional-fail",
        args=["echo intentional failure; exit 1"],
        command=["sh", "-c"],
        image="alpine:latest",
    )
