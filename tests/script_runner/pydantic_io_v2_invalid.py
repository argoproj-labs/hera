from typing import Annotated

from tests.helper import ARTIFACT_PATH

from hera.shared import global_config
from hera.workflows import Artifact, script
from hera.workflows.io.v2 import Input, Output

global_config.experimental_features["script_annotations"] = True
global_config.experimental_features["script_pydantic_io"] = True


class MultipleAnnotationInput(Input):
    str_path_artifact: Annotated[
        str,
        Artifact(name="str-path-artifact", path=ARTIFACT_PATH + "/str-path", loader=None),
        Artifact(name="str-path-artifact", path=ARTIFACT_PATH + "/path", loader=None),
    ]


class MultipleAnnotationOutput(Output):
    an_artifact: Annotated[str, Artifact(name="artifact-str-output"), Artifact(name="artifact-str-output")]


@script(constructor="runner")
def pydantic_input_invalid(
    my_input: MultipleAnnotationInput,
) -> str:
    return "Should not run"


@script(constructor="runner")
def pydantic_output_invalid() -> MultipleAnnotationOutput:
    return MultipleAnnotationOutput(an_artifact="test")
