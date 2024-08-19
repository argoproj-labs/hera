from hera.workflows import (
    Container,
    Parameter,
    Steps,
    Workflow,
    models as m,
)

with Workflow(generate_name="output-parameter-", entrypoint="output-parameter") as w:
    hello_world_to_file = Container(
        name="hello-world-to-file",
        image="busybox",
        command=["sh", "-c"],
        args=["sleep 1; echo -n hello world > /tmp/hello_world.txt"],
        outputs=Parameter(
            name="hello-param",
            value_from=m.ValueFrom(
                default="Foobar",
                path="/tmp/hello_world.txt",
            ),
        ),
    )
    print_message = Container(
        name="print-message",
        image="busybox",
        command=["echo"],
        args=["{{inputs.parameters.message}}"],
        inputs=Parameter(name="message"),
    )
    with Steps(name="output-parameter"):
        g = hello_world_to_file(name="generate-parameter")
        print_message(
            name="consume-parameter",
            arguments={"message": "{{steps.generate-parameter.outputs.parameters.hello-param}}"},
        )
