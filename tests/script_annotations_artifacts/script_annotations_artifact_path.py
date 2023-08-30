try:
    from typing import Annotated  # type: ignore
except ImportError:
    from typing_extensions import Annotated  # type: ignore

from pathlib import Path

from tests.helper import ARTIFACT_PATH

from hera.shared import global_config
from hera.workflows import Workflow, script
from hera.workflows.artifact import Artifact
from hera.workflows.steps import Steps

global_config.experimental_features["script_annotations"] = True
global_config.experimental_features["script_runner"] = True


@script(constructor="runner")
def read_artifact(an_artifact: Annotated[Path, Artifact(name="my-artifact", path=ARTIFACT_PATH, loader=None)]) -> str:
    return an_artifact.read_text()


with Workflow(generate_name="test-artifacts-", entrypoint="my_steps") as w:
    with Steps(name="my_steps") as s:
        read_artifact(arguments=[Artifact(name="my-artifact", from_="somewhere")])
