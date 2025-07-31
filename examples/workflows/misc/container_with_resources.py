from hera.workflows import Container, Resources, Workflow

with Workflow(generate_name="container-with-resources-", entrypoint="c") as w:
    Container(
        name="c",
        image="alpine:3.7",
        command=["sh", "-c"],
        args=["echo Hello, world!"],
        resources=Resources(cpu_request=1, memory_request="10Ki", ephemeral_request="10Ki"),
    )
