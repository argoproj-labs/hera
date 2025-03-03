from hera.workflows import Container, Steps, Workflow
from hera.workflows.models import LifecycleHook

with Workflow(generate_name="container-on-exit-", entrypoint="step-template") as w:
    exit_container = Container(
        name="exitContainer",
        image="busybox",
        command=["echo"],
        args=["goodbye world"],
    )
    hello_world = Container(
        name="hello-world",
        image="busybox",
        command=["echo"],
        args=["hello world"],
    )
    with Steps(name="step-template"):
        hello_world(name="stepA", hooks={"exit": LifecycleHook(template=exit_container.name)})
        hello_world(name="stepB", hooks={"exit": LifecycleHook(template=exit_container.name)})
