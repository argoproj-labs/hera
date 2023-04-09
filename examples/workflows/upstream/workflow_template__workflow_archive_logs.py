from hera.workflows import Container, Workflow

with Workflow(
    generate_name="archive-location-",
    entrypoint="whalesay",
    archive_logs=True,
) as w:
    Container(
        name="whalesay",
        image="docker/whalesay:latest",
        command=["cowsay"],
        args=["hello world"],
    )
