"""This example shows the various ways to use the `ArtifactLoader` enum to automatically load your Artifacts

You can load them as a `Path` of the file location, a `str` of the file contents, or any JSON type of the deserialised file contents.

Making the type of the function parameter `Optional` will make the `Artifact` itself optional, so the Hera Runner will load it only
if it exists.
"""

import json
from pathlib import Path
from typing import Annotated, Dict, Optional

from hera.workflows import Artifact, ArtifactLoader, Parameter, Steps, Workflow, script


@script(constructor="runner")
def output_dict_artifact(
    a_number: Annotated[int, Parameter(name="a_number")],
) -> Annotated[Dict[str, int], Artifact(name="an-artifact")]:
    return {"your-value": a_number}


@script(constructor="runner")
def artifact_loaders(
    a_file_as_path: Annotated[Path, Artifact(name="my-artifact-path", loader=None)],
    a_file_as_str: Annotated[str, Artifact(name="my-artifact-as-str", loader=ArtifactLoader.file)],
    a_file_as_json: Annotated[Dict, Artifact(name="my-artifact-as-json", loader=ArtifactLoader.json)],
    a_file_as_json_optional: Annotated[
        Optional[Dict], Artifact(name="my-optional-artifact", loader=ArtifactLoader.json)
    ] = None,
):
    assert a_file_as_path.read_text() == a_file_as_str
    assert json.loads(a_file_as_str) == a_file_as_json
    print(a_file_as_path)
    print(a_file_as_str)
    print(a_file_as_json)
    print(a_file_as_json_optional)


with Workflow(generate_name="artifact-loaders-", entrypoint="my-steps") as w:
    with Steps(name="my-steps") as s:
        out = output_dict_artifact(arguments={"a_number": 3})
        artifact_loaders(
            arguments={
                "my-artifact-path": out.get_artifact("an-artifact"),
                "my-artifact-as-str": out.get_artifact("an-artifact"),
                "my-artifact-as-json": out.get_artifact("an-artifact"),
            }
        )
