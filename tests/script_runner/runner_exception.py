"""Test the correctness of the Output annotations. The test uses the runner to check the outputs and if they save correctly to files."""

try:
    from typing import Annotated  # type: ignore
except ImportError:
    from typing_extensions import Annotated  # type: ignore

from hera.shared import global_config
from hera.workflows import Parameter, script
from hera.workflows.runner import RunnerException

global_config.experimental_features["script_annotations"] = True


@script()
def script_param() -> Annotated[int, Parameter(name="my-param")]:
    raise RunnerException(123)


@script()
def script_param_with_exit_code() -> Annotated[int, Parameter(name="my-param")]:
    raise RunnerException(123, exit_code=1)
