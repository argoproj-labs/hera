from hera.workflows import Container, Parameter, Workflow

with Workflow(
    generate_name="arguments-parameters-",
    entrypoint="print-message",
    arguments=Parameter(name="message", value="hello world"),
) as w:
    Container(
        name="print-message",
        image="busybox",
        command=["echo"],
        args=["{{inputs.parameters.message}}"],
        inputs=Parameter(name="message"),
    )
