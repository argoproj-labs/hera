"""This example shows how parameters can be passed into, within and out of a DAG."""

from pydantic import BaseModel
from typing_extensions import Annotated

from hera.shared import global_config
from hera.workflows import Input, Output, Parameter, Workflow

global_config.experimental_features["decorator_syntax"] = True


# Create a Workflow - we pass arguments here for the
# entrypoint (designated by the `set_entrypoint` decorator)
w = Workflow(
    generate_name="parameters-workflow-",
    arguments={"value_b": "a value for b!"},
)


class SetupConfig(BaseModel):
    a_param: str


class SetupOutput(Output):
    environment_parameter: str
    an_annotated_parameter: Annotated[int, Parameter(description="infer name from field")]
    setup_config: Annotated[
        SetupConfig, Parameter(name="setup-config")
    ]  # a Pydantic BaseModel can be a single input Parameter


@w.script()
def setup() -> SetupOutput:
    return SetupOutput(
        environment_parameter="linux",
        an_annotated_parameter=42,
        setup_config=SetupConfig(a_param="test"),
        result="Setting things up",
    )


class ConcatConfig(BaseModel):
    reverse: bool


class ConcatInput(Input):
    word_a: Annotated[str, Parameter(name="word_a")] = ""
    word_b: str
    concat_config: ConcatConfig = ConcatConfig(reverse=False)


@w.script()
def concat(concat_input: ConcatInput) -> Output:
    res = f"{concat_input.word_a} {concat_input.word_b}"
    if concat_input.concat_config.reverse:
        res = res[::-1]
    return Output(result=res)


class WorkerConfig(BaseModel):
    param_1: str
    param_2: str


class WorkerInput(Input):
    value_a: str = "my default"
    value_b: str
    an_int_value: int = 42
    a_basemodel: WorkerConfig = WorkerConfig(param_1="Hello", param_2="world")


class WorkerOutput(Output):
    result_value: str
    another_value: str


@w.set_entrypoint
@w.dag()
def worker(worker_input: WorkerInput) -> WorkerOutput:
    setup_task = setup()
    task_a = concat(
        ConcatInput(
            word_a=worker_input.value_a,
            word_b=setup_task.environment_parameter + str(setup_task.an_annotated_parameter),
        )
    )
    task_b = concat(ConcatInput(word_a=worker_input.value_b, word_b=setup_task.result))
    final_task = concat(ConcatInput(word_a=task_a.result, word_b=task_b.result))

    return WorkerOutput(
        result_value=final_task.result,
        another_value=str(setup_task.an_annotated_parameter),
    )
