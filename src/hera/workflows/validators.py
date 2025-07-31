"""Holds a collection of validators that are shared in V1."""

import re
from typing import Optional


def validate_name(name: str, max_length: Optional[int] = None, generate_name: bool = False) -> str:
    """DEPRECATED: Validates a name according to standard argo/kubernetes limitations.

    Unused throughout the Hera codebase. To be removed in a future version of Hera.

    Parameters
    ----------
    name: str
        The name which should be validated.
    max_length: Optional[int] = None
        Specify a maximum length of the name.
        Example: Kubernetes labels have a maximum length of 63 characters.
    generate_name: bool = False
        Whether the provided name is to be used as a prefix for name generation.
        If set, name is allowed to end in a single dot (.) or any number of hyphens (-).

    Raises:
    ------
    ValueError
        When the name is invalid according to specifications.

    Notes:
    -----
    Official doc on object names in Kubernetes:
    https://kubernetes.io/docs/concepts/overview/working-with-objects/names/
    """
    if max_length and len(name) > max_length:
        raise ValueError(f"Name is too long. Max length: {max_length}, found: {len(name)}")
    if "_" in name:
        raise ValueError("Name cannot include an underscore")
    if not generate_name and name.endswith((".", "-")):
        raise ValueError("Name cannot end with '.' nor '-', unless it is used as a prefix for name generation")

    pattern = r"[a-z0-9]([-a-z0-9]*[a-z0-9])?(\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*"
    if generate_name:
        pattern += r"(\.?|-*)"
    match_obj = re.fullmatch(pattern, name)
    if not match_obj:
        raise ValueError(f"Name is invalid: '{name}'. Regex used for validation is {pattern}")
    return name


def _validate_binary_units(value: str) -> None:
    """Validates the binary units of the given value.

    The given value is expected to satisfy a unit/value format that specifies a binary resource requirement such as 500Mi,
    1Gi, etc.

    Parameters
    ----------
    value: str
        The value to validate the binary unit of. The supported units are ['Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei']. Note that the units are case sensitive.

    Raises:
    ------
    ValueError
        When the identified unit is not a supported one.
    """
    pattern = r"^\s*(\d+(?:\.\d+)?)([KMGTPE]i)\s*$"
    if not re.match(pattern, value):
        raise ValueError(
            f"Invalid binary unit for input: {value}. Supported units are ['Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei']."
        )


def _validate_decimal_units(value: str) -> None:
    """Validates the decimal units of the given value.

    The given value is expected to satisfy a unit/value format that specifies a decimal resource requirement such as 500m,
    2k, etc. Note that the units are optional and accepts values such as int and float values in string e.g. "0.5" and "1".

    Parameters
    ----------
    value: str
        The value to validate the decimal unit of. The supported units are ['m', 'k', 'M', 'G', 'T', 'P', 'E']. Note that the units are case sensitive.

    Raises:
    ------
    ValueError
        When the identified unit is not a supported one.
    """
    pattern = r"^\s*(\d+(?:\.\d+)?)([mkMGTPE]?)\s*$"
    if not re.match(pattern, value):
        raise ValueError(
            f"Invalid decimal unit for input: {value}. Supported units are ['m', 'k', 'M', 'G', 'T', 'P', 'E']."
        )


validate_storage_units = _validate_binary_units
validate_memory_units = _validate_binary_units
validate_cpu_units = _validate_decimal_units
