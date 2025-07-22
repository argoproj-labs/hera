from hera.workflows import DAG, Container, Task, Workflow
from hera.workflows.models import IntOrString, RetryStrategy

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    generate_name="dag-primay-branch-",
    entrypoint="statis",
) as w:
    Container(
        name="a",
        args=["hello world"],
        command=["echo"],
        image="busybox",
    )
    Container(
        name="b",
        retry_strategy=RetryStrategy(
            limit=IntOrString(
                __root__="2",
            ),
        ),
        args=["sleep 30; echo haha"],
        command=["sh", "-c"],
        image="alpine:latest",
    )
    Container(
        name="c",
        retry_strategy=RetryStrategy(
            limit=IntOrString(
                __root__="3",
            ),
        ),
        args=["echo intentional failure; exit 2"],
        command=["sh", "-c"],
        image="alpine:latest",
    )
    Container(
        name="d",
        args=["hello world"],
        command=["echo"],
        image="busybox",
    )
    with DAG(
        name="statis",
        fail_fast=False,
    ) as invocator:
        Task(
            name="A",
            template="a",
        )
        Task(
            name="B",
            template="b",
            depends="A",
        )
        Task(
            name="C",
            template="c",
            depends="A",
        )
        Task(
            name="D",
            template="d",
            depends="B",
        )
        Task(
            name="E",
            template="d",
            depends="D",
        )
