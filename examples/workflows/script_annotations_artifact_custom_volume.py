"""This example will reuse the outputs volume across script steps."""


from hera.workflows.artifact import ArtifactLoader
from hera.workflows.volume import Volume

try:
    from typing import Annotated  # type: ignore
except ImportError:
    from typing_extensions import Annotated  # type: ignore


from hera.shared import global_config
from hera.workflows import (
    Artifact,
    EmptyDirVolume,
    Parameter,
    RunnerScriptConstructor,
    Steps,
    Workflow,
    models as m,
    script,
)

global_config.experimental_features["script_annotations"] = True
global_config.experimental_features["script_runner"] = True


@script(
    constructor=RunnerScriptConstructor(
        outputs_directory="/mnt/empty/dir",
        volume_for_outputs=EmptyDirVolume(name="my-empty-dir"),
    ),
)
def output_artifact_empty_dir(
    a_number: Annotated[int, Parameter(name="a_number")],
) -> Annotated[int, Artifact(name="successor_out")]:
    return a_number + 1


@script(
    constructor=RunnerScriptConstructor(),  # Has no outputs
)
def use_artifact(
    successor_in: Annotated[
        int,
        Artifact(name="successor_in", loader=ArtifactLoader.json),
    ]
):
    print(successor_in)


@script(
    constructor=RunnerScriptConstructor(outputs_directory="/mnt/here"),
    volume_mounts=[
        m.VolumeMount(name="my-vol", mount_path="/mnt/here")
    ],  # Mounting volume created outside of this script
)
def output_artifact_existing_vol(
    a_number: Annotated[int, Parameter(name="a_number")],
) -> Annotated[int, Artifact(name="successor_out")]:
    return a_number + 1


@script(
    constructor=RunnerScriptConstructor(),  # no outputs
    volume_mounts=[
        m.VolumeMount(name="my-vol", mount_path="/mnt/here")
    ],  # Mounting volume created outside of this script
)
def use_artifact_existing_vol(
    successor_in: Annotated[
        int, Artifact(name="successor_in", path="/mnt/here/artifacts/successor_out", loader=ArtifactLoader.json)
    ],
):
    print(successor_in)


with Workflow(
    generate_name="test-output-annotations-",
    entrypoint="my-steps",
    volumes=[Volume(name="my-vol", size="1Gi")],
) as w:
    with Steps(name="my-steps") as s:
        out_to_empty_dir = output_artifact_empty_dir(arguments={"a_number": 3})
        use_artifact(arguments=[out_to_empty_dir.get_artifact("successor_out").with_name("successor_in")])

        out_to_my_vol = output_artifact_existing_vol(arguments={"a_number": 3})
        use_artifact_existing_vol()
