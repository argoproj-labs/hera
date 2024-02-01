"""Module that holds the underlying base Pydantic models for Hera objects."""

from typing import TYPE_CHECKING, Any, Dict, Literal, Type

_PYDANTIC_VERSION: Literal[1, 2] = 1
# The pydantic v1 interface is used for both pydantic v1 and v2 in order to support
# users across both versions.

try:
    from pydantic.v1 import (  # type: ignore
        Field,
        ValidationError,
        root_validator,
        validator,
    )

    _PYDANTIC_VERSION = 2
except (ImportError, ModuleNotFoundError):
    from pydantic import (  # type: ignore[assignment,no-redef]
        Field,
        ValidationError,
        root_validator,
        validator,
    )

    _PYDANTIC_VERSION = 1


# TYPE_CHECKING-guarding specifically the `BaseModel` import helps the type checkers
# provide proper type checking to models. Without this, both mypy and pyright lose
# native pydantic hinting for `__init__` arguments.
if TYPE_CHECKING:
    from pydantic import BaseModel as PydanticBaseModel
else:
    try:
        from pydantic.v1 import BaseModel as PydanticBaseModel  # type: ignore
    except (ImportError, ModuleNotFoundError):
        from pydantic import BaseModel as PydanticBaseModel  # type: ignore[assignment,no-redef]


def get_fields(cls: Type[PydanticBaseModel]) -> Dict[str, Any]:
    """Centralize access to __fields__."""
    try:
        return cls.model_fields  # type: ignore
    except AttributeError:
        return cls.__fields__  # type: ignore


__all__ = [
    "BaseModel",
    "Field",
    "PydanticBaseModel",  # Export for serialization.py to cover user-defined models
    "ValidationError",
    "root_validator",
    "validator",
]


class BaseModel(PydanticBaseModel):
    class Config:
        """Config class dictates the behavior of the underlying Pydantic model.

        See Pydantic documentation for more info.
        """

        allow_population_by_field_name = True
        """support populating Hera object fields via keyed dictionaries"""

        allow_mutation = True
        """supports mutating Hera objects post instantiation"""

        use_enum_values = True
        """supports using enums, which are then unpacked to obtain the actual `.value`, on Hera objects"""

        arbitrary_types_allowed = True
        """supports specifying arbitrary types for any field to support Hera object fields processing"""

        smart_union = True
        """uses smart union for matching a field's specified value to the underlying type that's part of a union"""
