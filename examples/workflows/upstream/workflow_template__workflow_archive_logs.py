from hera.workflows import Container, Workflow

with Workflow(
    generate_name="archive-location-",
    entrypoint="hello-world",
    archive_logs=True,
) as w:
    Container(
        name="hello-world",
        image="busybox",
        command=["echo"],
        args=["hello world"],
    )
