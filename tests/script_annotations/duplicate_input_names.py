from typing import Annotated

from hera.workflows import Parameter, Workflow, script


@script(constructor="runner")
def duplicate_input_names(
    my_int: Annotated[int, Parameter(name="same-name")],
    my_other_int: Annotated[int, Parameter(name="same-name")],
) -> None:
    pass


with Workflow(generate_name="duplicate-input-") as w:
    duplicate_input_names()
