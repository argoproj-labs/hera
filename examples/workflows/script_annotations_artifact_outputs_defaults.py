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
    Parameter,
    Steps,
    Workflow,
    models as m,
    script,
)

global_config.experimental_features["script_annotations"] = True
global_config.experimental_features["script_runner"] = True


@script(constructor="runner")
def output_artifact(
    a_number: Annotated[int, Parameter(name="a_number")],
) -> Annotated[int, Artifact(name="successor_out")]:
    return a_number + 1


@script(constructor="runner")
def use_artifact(
    successor_in: Annotated[
        int,
        Artifact(
            name="successor_in",
            path="/tmp/file",
            loader=ArtifactLoader.json,
        ),
    ]
):
    print(successor_in)


with Workflow(
    generate_name="test-output-annotations-",
    entrypoint="my-steps",
    volumes=[Volume(name="my-vol", size="1Gi")],
) as w:
    with Steps(name="my-steps") as s:
        out = output_artifact(arguments={"a_number": 3})
        use_artifact(arguments=[out.get_artifact("successor_out").with_name("successor_in")])
