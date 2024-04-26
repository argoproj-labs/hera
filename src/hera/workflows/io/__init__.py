"""Hera IO models."""

from pydantic import VERSION

if VERSION.split(".")[0] == "2":
    from hera.workflows.io.v2 import RunnerInput, RunnerOutput
else:
    from hera.workflows.io.v1 import RunnerInput, RunnerOutput  # type: ignore

__all__ = [
    "RunnerInput",
    "RunnerOutput",
]
