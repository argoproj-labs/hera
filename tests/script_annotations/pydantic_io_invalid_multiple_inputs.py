import sys
from typing import Annotated

from hera.shared import global_config
from hera.workflows import Parameter, Workflow, script

if sys.version_info >= (3, 14):
    from hera.workflows.io.v2 import Input
else:
    from hera.workflows.io.v1 import Input


global_config.experimental_features["script_annotations"] = True
global_config.experimental_features["script_pydantic_io"] = True


class ParamOnlyInput(Input):
    my_int: int = 1
    my_annotated_int: Annotated[int, Parameter(name="another-int", description="my desc")] = 42


@script(constructor="runner")
def pydantic_multiple_inputs(
    my_obj: ParamOnlyInput,
    my_inline_int: int,
) -> None:
    pass


with Workflow(generate_name="pydantic-invalid-inputs-") as w:
    pydantic_multiple_inputs()
