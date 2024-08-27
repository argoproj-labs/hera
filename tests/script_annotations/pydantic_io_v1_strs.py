import sys
from pathlib import Path

if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated

from hera.workflows import Parameter, Workflow, script

try:
    from hera.workflows.io.v2 import (  # type: ignore
        Input,
        Output,
    )
except ImportError:
    from hera.workflows.io.v1 import (  # type: ignore
        Input,
        Output,
    )


class ParamOnlyInput(Input):
    my_str: str
    my_empty_default_str: str = ""
    my_annotated_str: Annotated[str, Parameter(name="alt-name")] = "hello world!"


class ParamOnlyOutput(Output):
    my_output_str: str = "my-default-str"
    another_output: Annotated[Path, Parameter(name="second-output")]


@script(constructor="runner")
def pydantic_io_params(
    my_input: ParamOnlyInput,
) -> ParamOnlyOutput:
    pass


with Workflow(generate_name="pydantic-io-") as w:
    pydantic_io_params()
