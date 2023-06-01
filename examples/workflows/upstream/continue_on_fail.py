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
    whalesay = Container(
        name="whalesay",
        image="docker/whalesay:latest",
        command=["cowsay"],
        args=["hello world"],
    )
    intentional_fail = Container(
        name="intentional-fail",
        image="alpine:latest",
        command=["sh", "-c"],
        args=["echo intentional failure; exit 1"],
    )
    with Steps(name="workflow-ignore") as steps:
        whalesay(name="A")
        with steps.parallel():
            whalesay(name="B")
            intentional_fail(name="C", continue_on=m.ContinueOn(failed=True))
        whalesay(name="D")
