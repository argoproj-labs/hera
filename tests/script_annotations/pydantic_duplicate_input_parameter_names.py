from hera.shared import global_config
from hera.workflows import Parameter, Workflow, script
from hera.workflows.io import RunnerInput

try:
    from typing import Annotated  # type: ignore
except ImportError:
    from typing_extensions import Annotated  # type: ignore

global_config.experimental_features["script_annotations"] = True
global_config.experimental_features["script_pydantic_io"] = True


class ParamOnlyInput(RunnerInput):
    my_int: int = 1
    my_annotated_int: Annotated[int, Parameter(name="another-int", description="my desc")] = 42


@script(constructor="runner")
def pydantic_duplicate_input_names(
    my_obj: ParamOnlyInput,
    my_other_obj: ParamOnlyInput,
) -> None:
    pass


with Workflow(generate_name="pydantic-duplicate-input-") as w:
    pydantic_duplicate_input_names()
