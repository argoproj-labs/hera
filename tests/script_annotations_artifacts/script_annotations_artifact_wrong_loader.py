try:
    from typing import Annotated  # type: ignore
except ImportError:
    from typing_extensions import Annotated  # type: ignore


from tests.helper import ARTIFACT_PATH

from hera.shared import global_config
from hera.workflows import Workflow, script
from hera.workflows.artifact import Artifact
from hera.workflows.steps import Steps

global_config.experimental_features["script_annotations"] = True
global_config.experimental_features["script_runner"] = True


@script(constructor="runner")
def read_artifact(
    an_artifact: Annotated[str, Artifact(name="my-artifact", path=ARTIFACT_PATH, loader="a different loader")]
) -> str:
    return an_artifact


with Workflow(generate_name="test-artifacts-", entrypoint="my-steps") as w:
    with Steps(name="my-steps") as s:
        read_artifact(arguments=[Artifact(name="my-artifact", from_="somewhere")])
