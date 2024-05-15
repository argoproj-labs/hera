"""Pydantic V1 input/output models for the Hera runner."""

from typing import Any

from hera.shared._pydantic import BaseModel
from hera.workflows.io._io_mixins import InputMixin, OutputMixin


class Input(InputMixin, BaseModel):
    """Input model usable by the Hera Runner.

    Input is a Pydantic model which users can create a subclass of. When a subclass
    of Input is used as a function parameter type, Hera will take the fields of the
    user's subclass to create template input parameters and artifacts. See the example
    for the script_pydantic_io experimental feature.
    """


class Output(OutputMixin, BaseModel):
    """Output model usable by the Hera Runner.

    Output is a Pydantic model which users can create a subclass of. When a subclass
    of Output is used as a function return type, Hera will take the fields of the
    user's subclass to create template output parameters and artifacts. See the example
    for the script_pydantic_io experimental feature.
    """

    exit_code: int = 0
    result: Any = None
