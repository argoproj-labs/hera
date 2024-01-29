import pytest

from hera.workflows.converters import _convert_binary_units, _convert_decimal_units


@pytest.mark.parametrize(
    "value, expected",
    [
        ("500m", 0.5),
        ("2k", 2000.0),
        ("1.5M", 1500000.0),
        ("42", 42.0),
    ],
)
def test_convert_decimal_units(value, expected):
    assert expected == _convert_decimal_units(value)


@pytest.mark.parametrize(
    "value, expected",
    [
        ("500Ki", 512000.0),
        ("1Mi", 1048576.0),
        ("2Gi", 2147483648.0),
        ("42", 42.0),
        ("0.5", 0.5),
    ],
)
def test_convert_binary_units(value, expected):
    assert expected == _convert_binary_units(value)


@pytest.mark.parametrize(
    "value",
    [
        "1.5Z",
        "abc",
        "1.5Ki",
        "1.5Mi",
    ],
)
def test_convert_decimal_units_invalid(value):
    with pytest.raises(ValueError, match="Invalid decimal units"):
        _convert_decimal_units(value)


@pytest.mark.parametrize(
    "value",
    [
        "1.5Z",
        "abc",
        "500m",
        "2k",
    ],
)
def test_convert_binary_units_invalid(value):
    with pytest.raises(ValueError, match="Invalid binary units"):
        _convert_binary_units(value)
