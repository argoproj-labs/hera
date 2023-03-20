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
    )

    with Steps(name="hello-hello-hello") as s:
        whalesay(
            name="hello1",
            arguments=[Parameter(name="message", value="hello1")],
        )

        with s.parallel():
            whalesay(
                name="hello2a",
                arguments=[Parameter(name="message", value="hello2a")],
            )
            whalesay(
                name="hello2b",
                arguments=[Parameter(name="message", value="hello2b")],
            )
