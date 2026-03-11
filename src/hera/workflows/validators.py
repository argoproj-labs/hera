"""Holds a collection of validators that are shared in V1."""

import re


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
