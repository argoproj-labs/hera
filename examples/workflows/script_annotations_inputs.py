try:
    from typing import Annotated  # type: ignore
except ImportError:
    from typing_extensions import Annotated  # type: ignore

from hera.shared import global_config
from hera.workflows import Artifact, Parameter, Workflow, script, Steps, ArtifactLoader

global_config.experimental_features["script_annotations"] = True
global_config.experimental_features["script_runner"] = True


@script(constructor="runner")
def echo_all(
    an_int: Annotated[int, Parameter(description="an_int parameter", default=1)],
    a_bool: Annotated[bool, Parameter(description="a_bool parameter", default=True)],
    a_string: Annotated[str, Parameter(description="a_string parameter", default="a")],
    # note that this artifact is loaded from tmp/file into an_artifact as a string
    an_artifact: Annotated[str, Artifact(name="my-artifact", path="/tmp/file", loader=ArtifactLoader.file)],
):
    print(an_int)
    print(a_bool)
    print(a_string)
    print(an_artifact)


with Workflow(generate_name="test-input-annotations-", entrypoint="my-steps") as w:
    with Steps(name="my-steps") as s:
        echo_all(
            arguments=[
                Parameter(name="an_int", value=1),
                Parameter(name="a_bool", value=True),
                Parameter(name="a_string", value="a"),
                Artifact(name="my-artifact", from_="somewhere"),
            ]
        )
