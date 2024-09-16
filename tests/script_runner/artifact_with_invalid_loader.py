"""This file causes a pydantic validation error when imported, so must be tested separately."""

from typing import Annotated

from tests.helper import ARTIFACT_PATH

from hera.shared import global_config
from hera.workflows import script
from hera.workflows.artifact import Artifact

global_config.experimental_features["script_annotations"] = True


@script(constructor="runner")
def invalid_loader(
    an_artifact: Annotated[str, Artifact(name="my-artifact", path=ARTIFACT_PATH, loader="a different loader")],
) -> str:
    return an_artifact
