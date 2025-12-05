"""Module that holds the underlying base Pydantic models for Hera objects."""

from collections import ChainMap
from inspect import get_annotations
from typing import Any, Dict, Type

from pydantic import (
    VERSION,
    BaseModel as PydanticBaseModel,
    Field,
    PrivateAttr,
    RootModel,
    ValidationError,
    model_validator as root_validator,
    validator,
)
from pydantic.fields import FieldInfo

_PYDANTIC_VERSION: int = int(VERSION.split(".")[0])


def get_fields(cls: Type[PydanticBaseModel]) -> Dict[str, FieldInfo]:
    """Centralize access to __fields__."""
    try:
        return cls.model_fields  # type: ignore
    except AttributeError:
        return cls.__fields__  # type: ignore


def model_dump(obj: PydanticBaseModel) -> Dict[str, Any]:
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
    "RootModel",
    "ValidationError",
    "root_validator",
    "validator",
]
