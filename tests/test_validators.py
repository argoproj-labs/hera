import pytest

from hera.validators import validate_storage_units


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
