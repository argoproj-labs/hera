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
        use_func_params_in_call=True,
    )
    print_message = Container(
        name="print-message",
        image="docker/whalesay:latest",
        command=["cowsay"],
        args=["{{inputs.parameters.message}}"],
        inputs=Parameter(name="message"),
        use_func_params_in_call=True,
    )
    with Steps(name="output-parameter"):
        g = whalesay().with_(name="generate-parameter")
        print_message(
            "{{steps.generate-parameter.outputs.parameters.hello-param}}",
        ).with_(
            name="consume-parameter",
        )
