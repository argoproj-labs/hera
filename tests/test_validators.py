from unittest import mock

import pytest

from hera.validators import validate_name, validate_storage_units


def test_validate_name():
    with pytest.raises(ValueError) as e:
        validate_name("test", max_length=1)
    assert str(e.value) == "Name is too long. Max length: 1, found: 4"
    with pytest.raises(ValueError) as e:
        validate_name("test_42")
    assert str(e.value) == "Name cannot include an underscore"
    with pytest.raises(ValueError) as e:
        validate_name("TEST")
    assert (
        str(e.value) == "Name is invalid: 'TEST'. Regex used for validation is "
        r"[a-z0-9]([-a-z0-9]*[a-z0-9])?(\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*"
    )
    with pytest.raises(ValueError):
        validate_name("test-")
    validate_name("test.a")
    validate_name("test-", generate_name=True)
    validate_name("test.", generate_name=True)
    with pytest.raises(ValueError) as e:
        validate_name("test.-", generate_name=True)
    assert (
        str(e.value) == "Name is invalid: 'test.-'. Regex used for validation is "
        r"[a-z0-9]([-a-z0-9]*[a-z0-9])?(\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*(\.?|-*)"
    )


def test_storage_validation_passes():
    values = ["1Ki", "1Mi", "12Gi", "1.0Ti", "1.42Pi", "0.42Ei"]
    for val in values:
        validate_storage_units(val)


def test_storage_validation_raises_value_error_on_unit_not_found():
    val = "42"
    with pytest.raises(ValueError) as e:
        validate_storage_units(val)
    assert str(e.value) == "could not extract units out of the passed in value"


def test_storage_validation_raises_assertion_error_on_unit_not_supported():
    val = "42whateverUnit"
    with pytest.raises(AssertionError) as e:
        validate_storage_units(val)
    assert str(e.value) == f"unsupported unit for parsed value {val}"
