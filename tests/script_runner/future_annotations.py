from __future__ import annotations

from typing import Annotated

from hera.workflows import Parameter, script


@script(constructor="runner")
def increment(value: int) -> int:
    return value + 1


@script(constructor="runner")
def annotated_parameter(
    value: Annotated[int, Parameter(name="renamed")],
) -> Annotated[int, Parameter(name="result")]:
    return value
