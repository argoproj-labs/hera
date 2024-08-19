from hera.workflows import (
    Container,
    Steps,
    Workflow,
    models as m,
)

with Workflow(
    generate_name="continue-on-fail-",
    entrypoint="workflow-ignore",
    parallelism=1,
) as w:
    hello_world = Container(
        name="hello-world",
        image="busybox",
        command=["echo"],
        args=["hello world"],
    )
    intentional_fail = Container(
        name="intentional-fail",
        image="alpine:latest",
        command=["sh", "-c"],
        args=["echo intentional failure; exit 1"],
    )
    with Steps(name="workflow-ignore") as steps:
        hello_world(name="A")
        with steps.parallel():
            hello_world(name="B")
            intentional_fail(name="C", continue_on=m.ContinueOn(failed=True))
        hello_world(name="D")
