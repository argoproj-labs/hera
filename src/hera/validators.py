"""Holds a collection of validators that are shared in V1"""
import re
from typing import Optional


def validate_name(name: str, max_length: Optional[int] = None, generate_name: bool = False) -> str:
    """Validates a name according to standard argo/kubernetes limitations

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

    Raises
    ------
    ValueError
        When the name is invalid according to specifications.

    Notes
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
    supported_units = ["Ki", "Mi", "Gi", "Ti", "Pi", "Ei"]

    pattern = r"[A-Za-z]+"
    unit_search = re.search(pattern, value)
    if not unit_search:
        raise ValueError("could not extract units out of the passed in value")
    else:
        unit = unit_search.group(0)
        assert unit in supported_units, f"unsupported unit for parsed value {value}"
