"""Hera IO models."""

from importlib.util import find_spec

if find_spec("pydantic.v1"):
    from hera.workflows.io.v2 import RunnerInput, RunnerOutput
else:
    from hera.workflows.io.v1 import RunnerInput, RunnerOutput  # type: ignore

__all__ = [
    "RunnerInput",
    "RunnerOutput",
]
