from hera.workflows import Container, Workflow

with Workflow(
    generate_name="hello-world-",
    image_pull_secrets="docker-registry-secret",
    entrypoint="hello-world",
) as w:
    Container(
        name="hello-world",
        image="busybox",
        command=["echo"],
        args=["hello world"],
    )
