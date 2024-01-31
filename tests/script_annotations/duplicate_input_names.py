from hera.shared import global_config
from hera.workflows import Parameter, Workflow, script

try:
    from typing import Annotated  # type: ignore
except ImportError:
    from typing_extensions import Annotated  # type: ignore

global_config.experimental_features["script_annotations"] = True
global_config.experimental_features["script_pydantic_io"] = True


@script(constructor="runner")
def duplicate_input_names(
    my_int: Annotated[int, Parameter(name="same-name")],
    my_other_int: Annotated[int, Parameter(name="same-name")],
) -> None:
    pass


with Workflow(generate_name="duplicate-input-") as w:
    duplicate_input_names()
