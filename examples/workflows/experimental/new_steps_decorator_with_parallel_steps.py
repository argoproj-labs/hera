"""This example shows the use of the new `steps` decorator, including parallel steps."""

from typing_extensions import Annotated

from hera.shared import global_config
from hera.workflows import Input, Output, Parameter, Workflow, parallel

global_config.experimental_features["decorator_syntax"] = True


w = Workflow(
    generate_name="steps-",
    arguments={"value_b": "a value for b!"},
)


class SetupOutput(Output):
    environment_parameter: str
    an_annotated_parameter: Annotated[int, Parameter(name="dummy-param")]


@w.script()
def setup() -> SetupOutput:
    return SetupOutput(environment_parameter="linux", an_annotated_parameter=42, result="Setting things up")


class ConcatInput(Input):
    word_a: Annotated[str, Parameter(name="word_a")] = ""
    word_b: str


@w.script()
def concat(concat_input: ConcatInput) -> Output:
    return Output(result=f"{concat_input.word_a} {concat_input.word_b}")


class WorkerInput(Input):
    value_a: str = "my default"
    value_b: str
    an_int_value: int = 42


class WorkerOutput(Output):
    value: str


@w.set_entrypoint
@w.steps()
def worker(worker_input: WorkerInput) -> WorkerOutput:
    setup_step = setup()
    with parallel():
        step_a = concat(
            ConcatInput(
                word_a=worker_input.value_a,
                word_b=setup_step.environment_parameter + str(setup_step.an_annotated_parameter),
            )
        )
        step_b = concat(ConcatInput(word_a=worker_input.value_b, word_b=setup_step.result))

    final_step = concat(ConcatInput(word_a=step_a.result, word_b=step_b.result))

    return WorkerOutput(value=final_step.result)
