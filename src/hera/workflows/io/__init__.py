"""Hera IO models."""

from typing import Type

from pydantic import VERSION

if VERSION.split(".")[0] == "2":
    from hera.workflows.io.v2 import Input, Output

    RunnerInput: Type = Input
    RunnerOutput: Type = Output
else:
    from hera.workflows.io.v1 import Input, Output  # type: ignore

    RunnerInput: Type = Input  # type: ignore
    RunnerOutput: Type = Output  # type: ignore

__all__ = [
    "Input",
    "Output",
    "RunnerInput",
    "RunnerOutput",
]
