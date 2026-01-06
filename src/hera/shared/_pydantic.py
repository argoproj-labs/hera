"""Module that holds the underlying base Pydantic models for Hera objects."""

from collections import ChainMap
from inspect import get_annotations
from typing import Any, Dict, Type

from pydantic import (
    VERSION,
    BaseModel as PydanticBaseModel,
    ConfigDict,
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
    # TODO[pydantic]: The following keys were removed: `allow_mutation`, `smart_union`.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(
        populate_by_name=True,
        allow_mutation=True,
        use_enum_values=True,
        arbitrary_types_allowed=True,
        smart_union=True,
    )


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
