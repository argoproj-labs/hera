from hera.workflows import (
    Container,
    Parameter,
    Steps,
    Workflow,
    models as m,
)

with Workflow(generate_name="output-parameter-", entrypoint="output-parameter") as w:
    whalesay = Container(
        name="whalesay",
        image="docker/whalesay:latest",
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
        image="docker/whalesay:latest",
        command=["cowsay"],
        args=["{{inputs.parameters.message}}"],
        inputs=Parameter(name="message"),
    )
    with Steps(name="output-parameter"):
        g = whalesay(name="generate-parameter")
        print_message(
            name="consume-parameter",
            arguments={"message": "{{steps.generate-parameter.outputs.parameters.hello-param}}"},
        )
