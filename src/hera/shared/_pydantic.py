"""Module that holds the underlying base Pydantic models for Hera objects."""

import sys
from collections import ChainMap
from typing import TYPE_CHECKING, Any, Dict, Type

if sys.version_info >= (3, 10):
    from inspect import get_annotations
else:
    from hera.shared._inspect import get_annotations

from pydantic import VERSION

# The pydantic v1 interface is used for both pydantic v1 and v2 in order to support
# users across both versions.
from pydantic.v1 import (
    BaseModel as PydanticBaseModel,
    Field,
    PrivateAttr,
    ValidationError,
    root_validator,
    validator,
)
from pydantic.v1.fields import FieldInfo

if TYPE_CHECKING:
    from pydantic import BaseModel as V2BaseModel

_PYDANTIC_VERSION: int = int(VERSION.split(".")[0])


def get_fields(cls: "Type[PydanticBaseModel] | Type[V2BaseModel]") -> Dict[str, FieldInfo]:
    """Centralize access to __fields__."""
    try:
        return cls.model_fields  # type: ignore
    except AttributeError:
        return cls.__fields__  # type: ignore


def model_dump(obj: "PydanticBaseModel | V2BaseModel") -> Dict[str, Any]:
    """Call model_dump, with V1 fallback."""
    if isinstance(obj, PydanticBaseModel):
        return obj.dict()
    return obj.model_dump(warnings="none")


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
