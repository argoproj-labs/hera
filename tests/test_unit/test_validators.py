import pytest

from hera.workflows.validators import _validate_binary_units, _validate_decimal_units


@pytest.mark.parametrize("value", ["500Ki", "1Mi", "2Gi", "1Ti", "1.5Pi", "1.5Ei"])
def test_validate_binary_units_valid(value):
    _validate_binary_units(value)


@pytest.mark.parametrize(
    "value, error_message",
    [("Mi", "Invalid binary unit"), ("5K", "Invalid binary unit"), ("Ti", "Invalid binary unit")],
)
def test_validate_binary_units_invalid(value, error_message):
    with pytest.raises(ValueError, match=error_message):
        _validate_binary_units(value)


@pytest.mark.parametrize("value", ["0.5", "1", "500m", "2k", "1.5M"])
def test_validate_decimal_units_valid(value):
    _validate_decimal_units(value)


@pytest.mark.parametrize(
    "value, error_message",
    [
        ("abc", "Invalid decimal unit"),
        ("K", "Invalid decimal unit"),
        ("2e", "Invalid decimal unit"),
        ("1.5Z", "Invalid decimal unit"),
    ],
)
def test_validate_decimal_units_invalid(value, error_message):
    with pytest.raises(ValueError, match=error_message):
        _validate_decimal_units(value)
