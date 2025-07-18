from pathlib import Path
from typing import Annotated

from pydantic import BaseModel
from tests.helper import ARTIFACT_PATH

from hera.shared import global_config
from hera.workflows import script
from hera.workflows.artifact import Artifact, ArtifactLoader

global_config.experimental_features["script_annotations"] = True


class MyArtifact(BaseModel):
    a: str = "a"
    b: str = "b"


@script(constructor="runner")
def json_object_loader(
    an_artifact: Annotated[MyArtifact, Artifact(name="my-artifact", path=ARTIFACT_PATH, loader=ArtifactLoader.json)],
) -> str:
    return an_artifact.a + an_artifact.b


@script(constructor="runner")
def no_loader(an_artifact: Annotated[Path, Artifact(name="my-artifact", path=ARTIFACT_PATH, loader=None)]) -> str:
    return an_artifact.read_text()


@script(constructor="runner")
def no_loader_as_string(
    an_artifact: Annotated[str, Artifact(name="my-artifact", path=ARTIFACT_PATH, loader=None)],
) -> str:
    """Getting the path as a string is allowed because the path in the Artifact class is a string"""
    return Path(an_artifact).read_text()


@script(constructor="runner")
def no_loader_invalid_type(
    an_artifact: Annotated[int, Artifact(name="my-artifact", path=ARTIFACT_PATH, loader=None)],
) -> str:
    # Type of an_artifact must fail validation and not be allowed to become a Path
    # The function code should not be reachable
    pass


@script(constructor="runner")
def file_loader(
    an_artifact: Annotated[str, Artifact(name="my-artifact", path=ARTIFACT_PATH, loader=ArtifactLoader.file)],
) -> str:
    return an_artifact


@script(constructor="runner")
def file_loader_default_path(
    an_artifact: Annotated[str, Artifact(loader=ArtifactLoader.file)],
) -> str:
    return an_artifact
