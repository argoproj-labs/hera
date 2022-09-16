import pytest
from argo_workflows import ApiTypeError

from hera import Parameter


def test_parameter():
    p = Parameter(name="o", value_from=dict(path="/test.txt", default="d"))
    assert p.name == "o"
    assert p.value_from
    assert p.value_from["path"] == "/test.txt"
    assert p.value_from["default"] == "d"


# def test_parameter_as_signature():
#     p = Parameter(name="i", value="v")


def test_parameter_as_output():
    p = Parameter(name="o", value_from=dict(path="/test.txt", default="d"))
    o = p.as_output()
    assert o.name == "o"
    assert o.value_from["path"] == "/test.txt"
    assert o.value_from["default"] == "d"


def test_parameter_as_input():
    p = Parameter(name="i", value="v")
    i = p.as_argument()
    assert i is not None
    assert i.name == "i"
    assert i.value == "v"


def test_parameter_as_input_fail():
    p = Parameter(name="i")
    with pytest.raises(ValueError) as e:
        p.as_argument()
    # assert str(e.value) == "Parameter cannot be interpreted as input as there is no `value` or `value_from`"


def test_parameter_with_default_value():
    p = Parameter(name="i", default="default_value")
    assert p.as_argument() is None
    assert p.as_input() is not None
    with pytest.raises(ApiTypeError):
        p.as_output()
