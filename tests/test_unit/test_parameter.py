from hera.workflows.parameter import Parameter
import pytest


def test_parameter_no_value_fails_to_string():
    param = Parameter(name="my_name", enum=[1, 2, 3])
    with pytest.raises(ValueError) as e:
        print(param)

    assert "Cannot represent `Parameter` as string as `value` is not set" in str(e.value)


def test_parameter_no_name_can_be_created():
    param = Parameter(value=3, enum=[1, 2, 3])
    assert param


def test_parameter_no_name_fails_as_input():
    param = Parameter(value=3, enum=[1, 2, 3])
    with pytest.raises(ValueError) as e:
        param.as_input()

    assert "name cannot be `None` or empty when used" in str(e.value)


def test_parameter_no_name_fails_as_argument():
    param = Parameter(value=3, enum=[1, 2, 3])
    with pytest.raises(ValueError) as e:
        param.as_argument()

    assert "name cannot be `None` or empty when used" in str(e.value)


def test_parameter_no_name_fails_as_output():
    param = Parameter(value=3, enum=[1, 2, 3])
    with pytest.raises(ValueError) as e:
        param.as_output()

    assert "name cannot be `None` or empty when used" in str(e.value)
