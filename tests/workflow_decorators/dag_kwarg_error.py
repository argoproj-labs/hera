from hera.shared import global_config
from hera.workflows import Input, Output, Workflow

global_config.experimental_features["decorator_syntax"] = True


w = Workflow(generate_name="my-workflow-")


class ConcatInput(Input):
    word_a: str
    word_b: str


@w.script()
def concat(concat_input: ConcatInput) -> Output:
    return Output(result=f"{concat_input.word_a} {concat_input.word_b}")


@w.set_entrypoint
@w.dag()
def worker() -> None:
    concat(concat_input=ConcatInput(word_a="hello", word_b="world"))
