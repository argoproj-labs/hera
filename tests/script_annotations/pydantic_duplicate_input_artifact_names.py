from hera.shared import global_config
from hera.workflows import Artifact, ArtifactLoader, Workflow, script
from hera.workflows.io.v1 import RunnerInput

try:
    from typing import Annotated  # type: ignore
except ImportError:
    from typing_extensions import Annotated  # type: ignore

global_config.experimental_features["script_annotations"] = True
global_config.experimental_features["script_pydantic_io"] = True


class ArtifactOnlyInput(RunnerInput):
    str_path_artifact: Annotated[str, Artifact(name="str-path-artifact", loader=None)]
    file_artifact: Annotated[str, Artifact(name="file-artifact", loader=ArtifactLoader.file)]


@script(constructor="runner")
def pydantic_multiple_inputs(
    my_obj: ArtifactOnlyInput,
    my_other_obj: ArtifactOnlyInput,
) -> None:
    pass


with Workflow(generate_name="pydantic-duplicate-input-") as w:
    pydantic_multiple_inputs()
