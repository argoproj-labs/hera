"""Holds a collection of validators that are shared in V1"""
import json
import re
from typing import Any, Union

from pydantic import BaseModel


def validate_storage_units(value: str) -> None:
    """Validates the units of the given value.

    The given value is expected to satisfy a unit/value format that specifies a resource requirement such as 500Mi,
    1Gi, etc.

    Parameters
    ----------
    value: str
        The value to validate the units of.

    Raises
    ------
    ValueError
        When the units cannot be extracted from the given value.
    AssertionError
        When the identified unit is not a supported one. The supported units are ['Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei'].
    """
    supported_units = ['Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei']

    pattern = r'[A-Za-z]+'
    unit_search = re.search(pattern, value)
    if not unit_search:
        raise ValueError('could not extract units out of the passed in value')
    else:
        unit = unit_search.group(0)
        assert unit in supported_units, f'unsupported unit for parsed value {value}'


def json_serializable(value: Union[BaseModel, Any]) -> True:  # type: ignore
    """Check if the given value is JSON serializable.

    Parameters
    ----------
    value: Union[BaseModel, Any]
        The value to check. Note that there's a union on the pydantic BaseModel and Any.

    Returns
    -------
    bool
        Whether the given value can be JSON serialized or not.
    """
    if not value:
        return True  # serialized as 'null'

    if isinstance(value, BaseModel):
        # BaseModels expose a .json() and .dict() on the model, which is serializable
        return True
    try:
        json.dumps(value)
    except (TypeError, OverflowError):
        return False
    return True
