try:
    from typing import Annotated  # type: ignore
except ImportError:
    from typing_extensions import Annotated  # type: ignore

from pathlib import Path

from hera.shared import global_config
from hera.workflows import Parameter, Workflow, script
from hera.workflows.steps import Steps

global_config.experimental_features["script_runner"] = True
global_config.experimental_features["script_annotations"] = True


@script(constructor="runner")
def script_param_in_fun_sig(
    a_number: Annotated[int, Parameter(name="a_number")],
    successor: Annotated[Path, Parameter(name="successor", output=True)],
):
    successor.save(a_number + 1)


with Workflow(generate_name="test-outputs-", entrypoint="my-steps") as w:
    with Steps(name="my-steps") as s:
        script_param_in_fun_sig(arguments={"a_number": 2})
        with s.parallel() as ps:
            script_param_in_fun_sig(arguments={"a_number": 3})
            script_param_in_fun_sig(arguments={"a_number": 4})
            script_param_in_fun_sig(arguments={"a_number": 5})
            script_param_in_fun_sig(arguments={"a_number": 6})
