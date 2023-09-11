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
        use_func_params_in_call=True,
    )
    with Steps(name="main") as s:
        whalesay(
            "hello1",
        ).with_(
            name="hello1",
            on_exit=exit_,
        )
        with s.parallel():
            whalesay(
                "hello2a",
            ).with_(
                name="hello2a",
                on_exit=exit_,
            )
            whalesay("hello2b").with_(
                name="hello2b",
                on_exit=exit_,
            )
