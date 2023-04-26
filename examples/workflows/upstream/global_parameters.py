from hera.workflows import Container, Parameter, Workflow

with Workflow(
    generate_name="global-parameters-",
    entrypoint="whalesay1",
    arguments=Parameter(name="message", value="hello world"),
) as w:
    Container(
        name="whalesay1",
        image="docker/whalesay:latest",
        command=["cowsay"],
        args=["{{workflow.parameters.message}}"],
    )
