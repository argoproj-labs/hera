from hera.workflows import Container, Parameter, Step, Steps, Workflow

with Workflow(
    generate_name="steps-",
    entrypoint="hello-hello-hello",
) as w:
    print_message = Container(
        name="print-message",
        inputs=[Parameter(name="message")],
        image="busybox",
        command=["echo"],
        args=["{{inputs.parameters.message}}"],
    )

    with Steps(name="hello-hello-hello") as s:
        Step(
            name="hello1",
            template=print_message,
            arguments=[Parameter(name="message", value="hello1")],
        )

        with s.parallel():
            Step(
                name="hello2a",
                template=print_message,
                arguments=[Parameter(name="message", value="hello2a")],
            )
            Step(
                name="hello2b",
                template=print_message,
                arguments=[Parameter(name="message", value="hello2b")],
            )
