from hera.workflows import (
    Container,
    EmptyDirVolume,
    UserContainer,
    Workflow,
    models as m,
)

with Workflow(
    generate_name="init-container-", entrypoint="init-container-example", volumes=EmptyDirVolume(name="foo")
) as w:
    init_container_example = Container(
        name="init-container-example",
        image="alpine:latest",
        command=["echo", "bye"],
        volume_mounts=[m.VolumeMount(name="foo", mount_path="/foo")],
        init_containers=[
            UserContainer(
                name="hello",
                image="alpine:latest",
                command=["echo", "hello"],
                mirror_volume_mounts=True,
            ),
        ],
    )
