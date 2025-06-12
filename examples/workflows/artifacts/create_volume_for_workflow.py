"""This example reuses a volume across scripts.

This avoids the performance loss of upload/download to your artifact storage.
Settings a `Volume` on the `Workflow` automatically creates a `volumeClaimTemplate` for the tasks to use.
"""

from typing import Annotated

from hera.workflows import (
    Artifact,
    NoneArchiveStrategy,
    Parameter,
    RunnerScriptConstructor,
    Steps,
    Workflow,
    models as m,
    script,
)
from hera.workflows.artifact import ArtifactLoader
from hera.workflows.volume import Volume


@script(
    constructor=RunnerScriptConstructor(outputs_directory="/mnt/here"),
    volume_mounts=[
        m.VolumeMount(name="my-vol", mount_path="/mnt/here")
    ],  # We mount the volume created by the Workflow
)
def output_artifact_existing_vol(
    a_number: Annotated[int, Parameter(name="a_number")],
) -> Annotated[int, Artifact(name="successor_out", archive=NoneArchiveStrategy())]:
    return a_number + 1


@script(
    constructor=RunnerScriptConstructor(),
    volume_mounts=[
        m.VolumeMount(name="my-vol", mount_path="/mnt/here")
    ],  # We mount the volume created by the Workflow
)
def use_artifact_existing_vol(
    successor_in: Annotated[
        int, Artifact(name="successor_in", path="/mnt/here/artifacts/successor_out", loader=ArtifactLoader.json)
    ],
):
    print(successor_in)


with Workflow(
    generate_name="create-volume-for-workflow-",
    entrypoint="my-steps",
    volumes=[Volume(name="my-vol", size="1Gi")],  # Creates a VolumeClaimTemplate (and thus the Volume itself)
) as w:
    with Steps(name="my-steps") as s:
        output_task = output_artifact_existing_vol(arguments={"a_number": 3})
        use_artifact_existing_vol(arguments={"successor_in": output_task.get_artifact("successor_out")})
