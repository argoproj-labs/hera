import pytest

from hera.workflows.validators import (
    _validate_binary_units,
    _validate_decimal_units,
    validate_cpu_units,
    validate_memory_units,
    validate_name,
    validate_storage_units,
)


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


@pytest.mark.parametrize(
    "name",
    [
        "valid-name",
        "valid-name123",
        "valid.name",
        "valid.name123",
        "a",
        "1",
        "valid-name-with-multiple-hyphens",
        "valid.name.with.multiple.dots",
        "valid-name.with-mixed.separators",
    ],
)
def test_validate_name_valid(name):
    """Test that valid names pass validation."""
    assert validate_name(name) == name


@pytest.mark.parametrize(
    "name, generate_name",
    [
        ("valid-name-", True),
        ("valid-name--", True),
        ("valid-name---", True),
        ("valid.name.", True),
    ],
)
def test_validate_name_valid_with_generate_name(name, generate_name):
    """Test that names ending with hyphens or dots are valid when generate_name is True."""
    assert validate_name(name, generate_name=generate_name) == name


@pytest.mark.parametrize(
    "name, error_message",
    [
        ("invalid_name", "cannot include an underscore"),
        ("invalid-name-", "cannot end with"),
        ("invalid.name.", "cannot end with"),
        ("-invalid-name", "Name is invalid"),
        (".invalid-name", "Name is invalid"),
        ("UPPERCASE-name", "Name is invalid"),
        ("", "Name is invalid"),
    ],
)
def test_validate_name_invalid(name, error_message):
    """Test that invalid names raise appropriate errors."""
    with pytest.raises(ValueError, match=error_message):
        validate_name(name)


def test_validate_name_too_long():
    """Test that names exceeding max_length raise an error."""
    name = "a" * 64
    with pytest.raises(ValueError, match="Name is too long"):
        validate_name(name, max_length=63)


def test_validate_storage_units_alias():
    """Test that validate_storage_units is an alias for _validate_binary_units."""
    assert validate_storage_units == _validate_binary_units


def test_validate_memory_units_alias():
    """Test that validate_memory_units is an alias for _validate_binary_units."""
    assert validate_memory_units == _validate_binary_units


def test_validate_cpu_units_alias():
    """Test that validate_cpu_units is an alias for _validate_decimal_units."""
    assert validate_cpu_units == _validate_decimal_units
