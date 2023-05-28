from hera.workflows import Container, Steps, Workflow

with Workflow(generate_name="container-on-exit-", entrypoint="step-template") as w:
    exit_container = Container(
        name="exitContainer",
        image="docker/whalesay",
        command=["cowsay"],
        args=["goodbye world"],
    )
    whalesay = Container(
        name="whalesay",
        image="docker/whalesay",
        command=["cowsay"],
        args=["hello world"],
    )
    with Steps(name="step-template"):
        whalesay(name="stepA", on_exit=exit_container)
        whalesay(name="stepB", on_exit=exit_container)
