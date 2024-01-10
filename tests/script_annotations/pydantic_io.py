from pathlib import Path

from hera.shared import global_config
from hera.workflows import Parameter, Steps, Workflow, script
from hera.workflows.artifact import Artifact
from hera.workflows.io import RunnerInput, RunnerOutput

try:
    from typing import Annotated  # type: ignore
except ImportError:
    from typing_extensions import Annotated  # type: ignore

global_config.experimental_features["script_annotations"] = True
global_config.experimental_features["script_pydantic_io"] = True


class MyInput(RunnerInput):
    my_int: int = 1
    my_annotated_int: Annotated[int, Parameter(name="another-int", description="my desc")] = 42


class MyOutput(RunnerOutput):
    my_output_str: str = "my-default-str"
    another_output: Annotated[Path, Parameter(name="second-output")]
    an_artifact: Annotated[Path, Artifact(name="artifact-output")]


@script(constructor="runner")
def pydantic_io_function(
    my_input: MyInput,
    another_param_inline: int,
) -> MyOutput:
    outputs = MyOutput(exit_code=10)
    return outputs


with Workflow(generate_name="pydantic-io-", entrypoint="my-steps") as w:
    with Steps(name="my-steps") as s:
        my_step = pydantic_io_function(
            arguments={
                "my_input": MyInput(my_param=2),
                "another_param_inline": 3,
            },
        )
