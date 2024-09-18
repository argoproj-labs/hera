"""Hera IO models."""

from pydantic import VERSION

if VERSION.split(".")[0] == "2":
    from hera.workflows.io.v2 import Input, Output

else:
    from hera.workflows.io.v1 import Input, Output  # type: ignore


__all__ = [
    "Input",
    "Output",
]
