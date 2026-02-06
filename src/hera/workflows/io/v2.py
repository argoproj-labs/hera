"""Pydantic V2 input/output models for the Hera runner.

Input/Output are only defined in this file if Pydantic v2 is installed.
"""

from typing import Any

from pydantic import (
    BaseModel as V2BaseModel,
    ConfigDict,
)

from hera.workflows._context import _context
from hera.workflows.io._io_mixins import InputMixin, OutputMixin


class _DeclaringEnabledModel(V2BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        frozen=False,
        use_enum_values=True,
        arbitrary_types_allowed=True,
    )

    def __new__(cls, **kwargs):
        if _context.declaring:
            # Intercept the declaration to avoid validation on the templated strings
            # We must then turn off declaring mode to be able to "model_construct" an instance
            # of the InputMixin subclass.
            _context.declaring = False
            instance = cls.model_construct(**kwargs)
            _context.declaring = True
            return instance
        else:
            return super(_DeclaringEnabledModel, cls).__new__(cls)

    def __init__(self, /, **kwargs):
        if _context.declaring:
            # Return in order to skip validation of `model_construct`ed instance
            return

        super().__init__(**kwargs)


class Input(InputMixin, _DeclaringEnabledModel):
    """Input model usable by the Hera Runner.

    Input is a Pydantic model which users can create a subclass of. When a subclass
    of Input is used as a function parameter type, the Hera Runner will take the fields
    of the user's subclass to create template input parameters and artifacts. See the example
    for the script_pydantic_io experimental feature.
    """


class Output(OutputMixin, _DeclaringEnabledModel):
    """Output model usable by the Hera Runner.

    Output is a Pydantic model which users can create a subclass of. When a subclass
    of Output is used as a function return type, the Hera Runner will take the fields
    of the user's subclass to create template output parameters and artifacts. See the example
    for the script_pydantic_io experimental feature.
    """

    exit_code: int = 0
    result: Any = None
