import sys
from typing import Annotated

from hera.workflows import Artifact, ArtifactLoader, Workflow, script

if sys.version_info >= (3, 14):
    from hera.workflows.io.v2 import Input
else:
    from hera.workflows.io.v1 import Input


class ArtifactOnlyInput(Input):
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
