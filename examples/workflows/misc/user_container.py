"""This example showcases the user of a user container with a volume mount."""

from hera.workflows import (
    DAG,
    UserContainer,
    Workflow,
    models as m,
    script,
)


@script(
    sidecars=[
        UserContainer(name="sidecar-name", volume_mounts=[m.VolumeMount(mount_path="/whatever", name="something")])
    ]
)
def foo():
    print("hi")


with Workflow(generate_name="sidecar-volume-mount-", entrypoint="d") as w:
    with DAG(name="d"):
        foo()
