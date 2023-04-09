from hera.workflows import Container, Workflow, models as m

with Workflow(
    generate_name="archive-location-",
    entrypoint="whalesay",
) as w:
    Container(
        name="whalesay",
        image="docker/whalesay:latest",
        command=["cowsay"],
        args=["hello world"],
        archive_location=m.ArtifactLocation(archive_logs=True),
    )
