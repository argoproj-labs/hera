"""Pydantic V1 input/output models for the Hera runner."""

import sys

# Pydantic V1 is not supported on Python 3.14.

if sys.version_info < (3, 14):
    from typing import Any

    from pydantic.v1 import BaseModel as V1BaseModel

    from hera.workflows._context import _context
    from hera.workflows.io._io_mixins import InputMixin, OutputMixin

    class _DeclaringEnabledModel(V1BaseModel):
        class Config:
            allow_population_by_field_name = True
            """support populating Hera object fields by their Field alias"""

            allow_mutation = True
            """supports mutating Hera objects post instantiation"""

            use_enum_values = True
            """supports using enums, which are then unpacked to obtain the actual `.value`, on Hera objects"""

            arbitrary_types_allowed = True
            """supports specifying arbitrary types for any field to support Hera object fields processing"""

            smart_union = True
            """uses smart union for matching a field's specified value to the underlying type that's part of a union"""

        def __new__(cls, **kwargs):
            if _context.declaring:
                # Intercept the declaration to avoid validation on the templated strings
                # We must then turn off declaring mode to be able to "construct" an instance
                # of the InputMixin subclass.
                _context.declaring = False
                instance = cls.construct(**kwargs)
                _context.declaring = True
                return instance
            else:
                return super(_DeclaringEnabledModel, cls).__new__(cls)

        def __init__(self, /, **kwargs):
            if _context.declaring:
                # Return in order to skip validation of `construct`ed instance
                return

            super().__init__(**kwargs)

    class Input(InputMixin, _DeclaringEnabledModel):
        """Input model usable by the Hera Runner.

        Input is a Pydantic model which users can create a subclass of. When a subclass
        of Input is used as a function parameter type, Hera will take the fields of the
        user's subclass to create template input parameters and artifacts. See the example
        for the script_pydantic_io experimental feature.
        """

    class Output(OutputMixin, _DeclaringEnabledModel):
        """Output model usable by the Hera Runner.

        Output is a Pydantic model which users can create a subclass of. When a subclass
        of Output is used as a function return type, Hera will take the fields of the
        user's subclass to create template output parameters and artifacts. See the example
        for the script_pydantic_io experimental feature.
        """

        exit_code: int = 0
        result: Any = None
