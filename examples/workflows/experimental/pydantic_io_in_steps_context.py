import sys
from typing import List

if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated


from hera.shared import global_config
from hera.workflows import Parameter, Steps, WorkflowTemplate, script
from hera.workflows.io.v1 import Input, Output

global_config.experimental_features["script_pydantic_io"] = True


class CutInput(Input):
    cut_after: Annotated[int, Parameter(name="cut-after")]
    strings: List[str]


class CutOutput(Output):
    first_strings: Annotated[List[str], Parameter(name="first-strings")]
    remainder: List[str]


class JoinInput(Input):
    strings: List[str]
    joiner: str


class JoinOutput(Output):
    joined_string: Annotated[str, Parameter(name="joined-string")]


@script(constructor="runner")
def cut(input: CutInput) -> CutOutput:
    return CutOutput(
        first_strings=input.strings[: input.cut_after],
        remainder=input.strings[input.cut_after :],
        exit_code=1 if len(input.strings) <= input.cut_after else 0,
    )


@script(constructor="runner")
def join(input: JoinInput) -> JoinOutput:
    return JoinOutput(joined_string=input.joiner.join(input.strings))


with WorkflowTemplate(generate_name="pydantic-io-in-steps-context-v1-", entrypoint="d") as w:
    with Steps(name="d"):
        cut_result = cut(CutInput(strings=["hello", "world", "it's", "hera"], cut_after=1))
        join(JoinInput(strings=cut_result.first_strings, joiner=" "))
