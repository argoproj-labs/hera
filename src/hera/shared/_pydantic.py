"""Module that holds the underlying base Pydantic models for Hera objects."""

from collections import ChainMap
from typing import TYPE_CHECKING, Any, Dict, Type

from pydantic import VERSION

try:
    from inspect import get_annotations  # type: ignore
except ImportError:
    from hera.shared._inspect import get_annotations  # type: ignore


_PYDANTIC_VERSION: int = int(VERSION.split(".")[0])
# The pydantic v1 interface is used for both pydantic v1 and v2 in order to support
# users across both versions.

if _PYDANTIC_VERSION == 2:
    from pydantic.v1 import (
        BaseModel as PydanticBaseModel,
        Field,
        PrivateAttr,
        ValidationError,
        root_validator,
        validator,
    )
    from pydantic.v1.fields import FieldInfo
else:
    from pydantic import (  # type: ignore[assignment,no-redef]
        BaseModel as PydanticBaseModel,
        Field,
        PrivateAttr,
        ValidationError,
        root_validator,
        validator,
    )
    from pydantic.fields import FieldInfo  # type: ignore[assignment,no-redef]


# TYPE_CHECKING-guarding specifically the `BaseModel` import helps the type
# checkers provide proper type checking to models. Without this, both mypy and
# pyright lose native pydantic hinting for `__init__` arguments.
#
# Now there can be 2 versions of `BaseModel` at runtime, but here we must choose
# one for the type checker, otherwise external type checkers as well as editors
# won't be able to do much. vscode for example would always give 2
# options when jumping to source instead of just picking one. Pydantic/Pylance
# wouldn't be able to do much.
#
# Since Hera's models are still using v1 API, that's the reasonable choice.
if TYPE_CHECKING:
    from pydantic.v1 import BaseModel as PydanticBaseModel
    from pydantic.v1.fields import FieldInfo


def get_fields(cls: Type[PydanticBaseModel]) -> Dict[str, FieldInfo]:
    """Centralize access to __fields__."""
    try:
        return cls.model_fields  # type: ignore
    except AttributeError:
        return cls.__fields__  # type: ignore


def get_field_annotations(cls: Type[PydanticBaseModel]) -> Dict[str, Any]:
    return {k: v for k, v in ChainMap(*(get_annotations(c) for c in cls.__mro__)).items()}


class BaseModel(PydanticBaseModel):
    class Config:
        """Config class dictates the behavior of the underlying Pydantic model.

        See Pydantic documentation for more info.
        """

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


__all__ = [
    "BaseModel",
    "Field",
    "FieldInfo",
    "PrivateAttr",
    "PydanticBaseModel",  # Export for serialization.py to cover user-defined models
    "ValidationError",
    "root_validator",
    "validator",
]
