from hera.shared import global_config
from hera.workflows import Input, Output, Workflow

global_config.experimental_features["script_annotations"] = True
global_config.experimental_features["script_pydantic_io"] = True


w = Workflow(generate_name="my-workflow-")


class SetupOutput(Output):
    environment_parameter: str


@w.script()
def setup() -> SetupOutput:
    return SetupOutput(environment_parameter="linux", result="Setting things up")


class ConcatInput(Input):
    word_a: str
    word_b: str


@w.script()
def concat(concat_input: ConcatInput) -> Output:
    return Output(result=f"{concat_input.word_a} {concat_input.word_b}")


class WorkerInput(Input):
    value_a: str
    value_b: str


class WorkerOutput(Output):
    value: str


@w.set_entrypoint
@w.dag()
def worker(worker_input: WorkerInput) -> WorkerOutput:
    setup_task = setup()
    task_a = concat(ConcatInput(word_a=worker_input.value_a, word_b=setup_task.environment_parameter))
    task_b = concat(ConcatInput(word_a=worker_input.value_b, word_b=setup_task.result))
    final_task = concat(ConcatInput(word_a=task_a.result, word_b=task_b.result))

    return WorkerOutput(value=final_task.result)
