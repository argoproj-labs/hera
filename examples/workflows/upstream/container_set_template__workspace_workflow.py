from hera.workflows import ContainerNode, ContainerSet, EmptyDirVolume, Parameter, Workflow
from hera.workflows.models import Artifact, ValueFrom, VolumeMount

with Workflow(
    generate_name="workspace-",
    entrypoint="main",
) as w:
    with ContainerSet(
        name="main",
        volumes=[EmptyDirVolume(name="workspace", mount_path="/workspace")],
        volume_mounts=[VolumeMount(name="workspace", mount_path="/workspace")],
        outputs=[
            Parameter(name="out", value_from=ValueFrom(path="/workspace/out")),
            Artifact(name="out", path="/workspace/out"),
        ],
    ):
        ContainerNode(
            name="a",
            image="argoproj/argosay:v2",
            args=["echo", "hi", "/workspace/out"],
        )
        ContainerNode(
            name="main",
            image="argoproj/argosay:v2",
        )
