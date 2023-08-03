try:
    from typing import Annotated  # type: ignore
except ImportError:
    from typing_extensions import Annotated  # type: ignore

from pydantic import BaseModel
from tests.helper import ARTIFACT_PATH

from hera.shared import global_config
from hera.workflows import Workflow, script
from hera.workflows.artifact import Artifact, ArtifactLoader
from hera.workflows.steps import Steps

global_config.experimental_features["script_annotations"] = True
global_config.experimental_features["script_runner"] = True


class MyArtifact(BaseModel):
    a = "a"
    b = "b"


@script()
def read_artifact(
    an_artifact: Annotated[MyArtifact, Artifact(name="my-artifact", path=ARTIFACT_PATH, loader=ArtifactLoader.json)]
) -> str:
    return an_artifact.a + an_artifact.b


with Workflow(generate_name="test-types-", entrypoint="my_steps") as w:
    with Steps(name="my_steps") as s:
        read_artifact(arguments=[Artifact(name="my-artifact", from_="somewhere")])
