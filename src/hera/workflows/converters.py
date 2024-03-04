"""Utility functions for converting binary and decimal units to float values."""

import re

_decimal_multipliers = {
    "m": 1e-3,
    "k": 1e3,
    "M": 1e6,
    "G": 1e9,
    "T": 1e12,
    "P": 1e15,
    "E": 1e18,
}

_binary_multipliers = {
    "Ki": 2**10,
    "Mi": 2**20,
    "Gi": 2**30,
    "Ti": 2**40,
    "Pi": 2**50,
    "Ei": 2**60,
}


def _convert_decimal_units(value: str) -> float:
    """Converts the given decimal units to a float value. If no unit is given, the value is multiplied by 1.

    Args:
        value (str): The value to convert the decimal units of. The supported units are ['m', 'k', 'M', 'G', 'T', 'P', 'E'].
        Note that the units are case sensitive.

    Raises:
        ValueError: When the identified unit is not a supported one.

    Returns:
        float: Float value of the given decimal units.
    """
    pattern = r"^\s*([+-]?\d+(?:\.\d+)?)([mkMGTPE]?)\s*$"
    matches = re.match(pattern, value)

    if matches:
        value, unit = matches.groups()
        return float(value) * _decimal_multipliers.get(unit, 1)
    else:
        raise ValueError(
            f"Invalid decimal units for input: {value}. Supported units are ['m', 'k', 'M', 'G', 'T', 'P', 'E']."
        )


def _convert_binary_units(value: str) -> float:
    """Converts the given binary units to a float value. If no unit is given, the value is multiplied by 1.

    Args:
        value (str): The value to convert the binary unit of. The supported units are ['Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei'].
        Note that the units are case sensitive.

    Raises:
        ValueError: When the identified unit is not a supported one.

    Returns:
        float: Float value of the given binary units.
    """
    pattern = r"^\s*([+-]?\d+(?:\.\d+)?)([KMGTPE]i)?\s*$"
    matches = re.match(pattern, value)

    if matches:
        value, unit = matches.groups()
        return float(value) * _binary_multipliers.get(unit, 1)
    else:
        raise ValueError(
            f"Invalid binary units for input: {value}. Supported units are ['Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei']."
        )


convert_memory_units = _convert_binary_units
convert_storage_units = _convert_binary_units
convert_cpu_units = _convert_decimal_units
