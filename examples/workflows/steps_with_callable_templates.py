from hera.workflows import (
    Container,
    Parameter,
    Steps,
    Workflow,
)

with Workflow(
    generate_name="callable-templates-",
    entrypoint="hello-world",
) as w:
    echo = Container(
        name="echo",
        image="alpine:3.7",
        command=["echo", "{{inputs.parameters.message}}"],
        inputs=[Parameter(name="message")],
    )

    with Steps(name="hello-world") as s:
        echo(name="hello1", arguments=[Parameter(name="message", value="hello1")])
        echo(name="hello2", arguments=[Parameter(name="message", value="hello2")])
