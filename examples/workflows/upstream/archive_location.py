from hera.workflows import (
    Container,
    Workflow,
)

with Workflow(
    generate_name="archive-location-",
    entrypoint="whalesay",
) as w:
    Container(
        name="whalesay",
        image="docker/whalesay:latest",
        command=["cowsay"],
        args=["hello world"],
        archive_location={"archive_logs": True},
    )
