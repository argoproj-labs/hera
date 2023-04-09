from hera.workflows import Container, Parameter, Workflow

with Workflow(
    generate_name="arguments-parameters-",
    entrypoint="whalesay",
    arguments=Parameter(name="message", value="hello world"),
) as w:
    Container(
        name="whalesay",
        image="docker/whalesay:latest",
        command=["cowsay"],
        args=["{{inputs.parameters.message}}"],
        inputs=Parameter(name="message"),
    )
