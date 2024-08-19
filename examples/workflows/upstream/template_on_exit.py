from hera.workflows import Container, Steps, Workflow

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
        hello_world(name="stepA", on_exit=exit_container)
        hello_world(name="stepB", on_exit=exit_container)
