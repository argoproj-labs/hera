from typing import Dict
import json
from pathlib import Path

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
def artifact_loaders(
    a_file_as_path: Annotated[Path, Artifact(name="my-artifact-path", loader=None)],
    a_file_as_str: Annotated[str, Artifact(name="my-artifact-as-str", loader=ArtifactLoader.file)],
    a_file_as_json: Annotated[Dict, Artifact(name="my-artifact-as-json", loader=ArtifactLoader.json)],
):
    assert a_file_as_path.read_text() == a_file_as_str
    assert json.loads(a_file_as_str) == a_file_as_json
    print(a_file_as_path)
    print(a_file_as_str)
    print(a_file_as_json)


with Workflow(generate_name="test-input-annotations-", entrypoint="my-steps") as w:
    with Steps(name="my-steps") as s:
        out = output_dict_artifact(arguments={"a_number": 3})
        artifact_loaders(
            arguments=[
                out.get_artifact("a_dict").with_name("my-artifact-path"),
                out.get_artifact("a_dict").with_name("my-artifact-as-str"),
                out.get_artifact("a_dict").with_name("my-artifact-as-json"),
            ]
        )
