from hera.workflows import Container, Parameter, Steps, Workflow

with Workflow(
    generate_name="exit-handler-step-level-",
    entrypoint="main",
) as w:
    exit_ = Container(
        name="exit",
        image="docker/whalesay",
        command=["cowsay"],
        args=["step cleanup"],
    )
    whalesay = Container(
        name="whalesay",
        inputs=[Parameter(name="message")],
        image="docker/whalesay",
        command=["cowsay"],
        args=["{{inputs.parameters.message}}"],
    )
    with Steps(name="main") as s:
        whalesay(
            name="hello1",
            arguments=[Parameter(name="message", value="hello1")],
            on_exit=exit_,
        )
        with s.parallel():
            whalesay(
                name="hello2a",
                arguments=[Parameter(name="message", value="hello2a")],
                on_exit=exit_,
            )
            whalesay(
                name="hello2b",
                arguments=[Parameter(name="message", value="hello2b")],
                on_exit=exit_,
            )
