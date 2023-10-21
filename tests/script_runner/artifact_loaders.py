try:
    from typing import Annotated  # type: ignore
except ImportError:
    from typing_extensions import Annotated  # type: ignore

from pathlib import Path

from pydantic import BaseModel
from tests.helper import ARTIFACT_PATH

from hera.shared import global_config
from hera.workflows import script
from hera.workflows.artifact import Artifact, ArtifactLoader

global_config.experimental_features["script_annotations"] = True
global_config.experimental_features["script_runner"] = True


class MyArtifact(BaseModel):
    a = "a"
    b = "b"


@script(constructor="runner")
def json_object_loader(
    an_artifact: Annotated[MyArtifact, Artifact(name="my-artifact", path=ARTIFACT_PATH, loader=ArtifactLoader.json)]
) -> str:
    return an_artifact.a + an_artifact.b


@script(constructor="runner")
def no_loader(an_artifact: Annotated[Path, Artifact(name="my-artifact", path=ARTIFACT_PATH, loader=None)]) -> str:
    return an_artifact.read_text()


@script(constructor="runner")
def file_loader(
    an_artifact: Annotated[str, Artifact(name="my-artifact", path=ARTIFACT_PATH, loader=ArtifactLoader.file)]
) -> str:
    return an_artifact


@script(constructor="runner")
def file_loader_default_path(
    an_artifact: Annotated[str, Artifact(name="my-artifact", loader=ArtifactLoader.file)]
) -> str:
    return an_artifact
