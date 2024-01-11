
from hera.shared import global_config
from hera.workflows import Parameter, Steps, Workflow, script
from hera.workflows.io import RunnerInput, RunnerOutput

try:
    from typing import Annotated  # type: ignore
except ImportError:
    from typing_extensions import Annotated  # type: ignore

global_config.experimental_features["script_annotations"] = True
global_config.experimental_features["script_pydantic_io"] = True


class MyInput(RunnerInput):
    my_required_int: int
    my_int: int = 1
    my_annotated_int: Annotated[int, Parameter(name="another-int", description="my desc")] = 42


class MyOutput(RunnerOutput):
    my_output_str: str = "my-default-str"
    # another_output: Annotated[Path, Parameter(name="second-output")]
    # an_artifact: Annotated[Path, Artifact(name="artifact-output")]


@script(constructor="runner")
def pydantic_io_function(
    my_input: MyInput,
    another_param_inline: int,
    another_annotated_param_inline: Annotated[str, Parameter(name="a-str-param")],
) -> MyOutput:
    outputs = MyOutput(exit_code=10)
    outputs.my_output_str = str(my_input.my_int)
    # outputs.another_output.write("foo")
    outputs.result = another_param_inline * 2

    return outputs


@script(constructor="runner")
def echo(
    my_output: str,
    another_param: str,
) -> None:
    print(my_output)
    print(another_param)


with Workflow(generate_name="pydantic-io-", entrypoint="my-steps") as w:
    with Steps(name="my-steps") as s:
        my_step = pydantic_io_function(
            arguments={
                "my_input": MyInput(my_param=2, my_required_int=1),
                "another_param_inline": 3,
            },
        )
        echo(
            arguments={
                "my_output": my_step.get_parameter("my_output_str"),
                "another_param": my_step.result,
            },
        )
