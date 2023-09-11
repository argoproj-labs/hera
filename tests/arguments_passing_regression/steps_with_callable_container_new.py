from hera.workflows import Container, Parameter, Steps, Workflow

with Workflow(
    generate_name="steps-",
    entrypoint="hello-hello-hello",
) as w:
    whalesay = Container(
        name="whalesay",
        inputs=[Parameter(name="message")],
        image="docker/whalesay",
        command=["cowsay"],
        args=["{{inputs.parameters.message}}"],
        use_func_params_in_call=True,
    )

    with Steps(name="hello-hello-hello") as s:
        whalesay(
            "hello1",
        ).with_(name="hello1")

        with s.parallel():
            whalesay(
                "hello2a",
            ).with_(
                name="hello2a",
            )
            whalesay(
                "hello2b",
            ).with_(
                name="hello2b",
            )
