"""Holds a collection of validators that are shared in V1"""
import re
from typing import Optional


def validate_name(name: Optional[str] = None, max_length: Optional[int] = None, generate_name: str = None):
    """Validates a name according to standard argo/kubernetes limitations

    Parameters
    ----------
    name: str
        The name which should be validated.
    max_length: Optional[int] = None
        Specify a maximum length of the name.
        Example: Kubernetes labels have a maximum length of 63 characters.
    generate_name: str = False
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
    if name is None and generate_name is None:
        raise ValueError("At least one of `name` or `generate_name` must be specified")

    if max_length and name is not None and len(name) > max_length:
        raise ValueError(f"Name is too long. Max length: {max_length}, found: {len(name)}")
    if name is not None and "_" in name:
        raise ValueError("Name cannot include an underscore")
    if generate_name is None and name is not None and name.endswith((".", "-")):
        raise ValueError("Name cannot end with '.' nor '-', unless it is used as a prefix for name generation")

    pattern = r"[a-z0-9]([-a-z0-9]*[a-z0-9])?(\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*"
    if generate_name is not None:
        pattern += r"(\.?|-*)"

    if name is not None:
        match_obj = re.fullmatch(pattern, name)
        if not match_obj:
            raise ValueError(f"Name is invalid: '{name}'. Regex used for validation is {pattern}")


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
