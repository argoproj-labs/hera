from typing import Dict

try:
    from typing import Annotated  # type: ignore
except ImportError:
    from typing_extensions import Annotated  # type: ignore

from hera.shared import global_config
from hera.workflows import Artifact, Parameter, Workflow, script, Steps, ArtifactLoader

global_config.experimental_features["script_annotations"] = True
global_config.experimental_features["script_runner"] = True


@script(constructor="runner")
def output_dict_artifact(
    a_number: Annotated[int, Parameter(name="a_number")],
) -> Annotated[Dict[str, int], Artifact(name="a_dict")]:
    return {"your-value": a_number}


@script(constructor="runner")
def echo_all(
    an_int: Annotated[int, Parameter(description="an_int parameter", default=1)],
    a_bool: Annotated[bool, Parameter(description="a_bool parameter", default=True)],
    a_string: Annotated[str, Parameter(description="a_string parameter", default="a")],
    # note that this artifact is loaded from /tmp/file into an_artifact as a string
    an_artifact: Annotated[str, Artifact(name="my-artifact", path="/tmp/file", loader=ArtifactLoader.file)],
    # note that this automatically uses the path /tmp/hera/inputs/artifacts/my-artifact-no-path
    an_artifact_no_path: Annotated[str, Artifact(name="my-artifact-no-path", loader=ArtifactLoader.file)],
):
    print(an_int)
    print(a_bool)
    print(a_string)
    print(an_artifact)
    print(an_artifact_no_path)


with Workflow(generate_name="test-input-annotations-", entrypoint="my-steps") as w:
    with Steps(name="my-steps") as s:
        out = output_dict_artifact(arguments={"a_number": 3})
        echo_all(
            arguments=[
                Parameter(name="an_int", value=1),
                Parameter(name="a_bool", value=True),
                Parameter(name="a_string", value="a"),
                out.get_artifact("a_dict").with_name("my-artifact"),
                out.get_artifact("a_dict").with_name("my-artifact-no-path"),
            ]
        )
