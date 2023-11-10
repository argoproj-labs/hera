"""The unit tests of the Parameter class, covering the name: Optional[str] behaviour."""

import pytest

from hera.workflows.models import Parameter as ModelParameter
from hera.workflows.parameter import Parameter


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


@pytest.mark.parametrize(
    "value,default,enum,expected_built_parameter",
    (
        pytest.param(
            "value-string",
            "default-string",
            ["value-string", "default-string", "another-enum-string"],
            ModelParameter(
                name="test",
                value="value-string",
                default="default-string",
                enum=["value-string", "default-string", "another-enum-string"],
            ),
            id="strings",
        ),
        pytest.param(
            1,
            2,
            [1, 2],
            ModelParameter(name="test", value="1", default="2", enum=["1", "2"]),
            id="numbers",
        ),
        pytest.param(
            True,
            False,
            [True, False, None],
            ModelParameter(name="test", value="true", default="false", enum=["true", "false", "null"]),
            id="bools-and-none",
        ),
        pytest.param(
            {"my-key": "my-value"},
            {"my-key": "my-default"},
            [{"my-key": "my-value"}, {"my-key": "my-default"}],
            ModelParameter(
                name="test",
                value='{"my-key": "my-value"}',
                default='{"my-key": "my-default"}',
                enum=['{"my-key": "my-value"}', '{"my-key": "my-default"}'],
            ),
            id="arbitrary-dict",
        ),
        pytest.param(
            ["my-value1", "my-value2"],
            ["my-default-value"],
            [["my-value1", "my-value2"], ["my-default-value"], ["another", "enum", "value"]],
            ModelParameter(
                name="test",
                value='["my-value1", "my-value2"]',
                default='["my-default-value"]',
                enum=['["my-value1", "my-value2"]', '["my-default-value"]', '["another", "enum", "value"]'],
            ),
            id="arbitrary-list",
        ),
    ),
)
def test_parameter_values_serialization(value, default, enum, expected_built_parameter):
    assert (
        Parameter(
            name="test",
            value=value,
            default=default,
            enum=enum,
        ).as_input()
        == expected_built_parameter
    )
