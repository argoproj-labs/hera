"""The unit tests of the Parameter class, covering the name: Optional[str] behaviour."""

import pytest

from hera.workflows._mixins import ArgumentsMixin
from hera.workflows.models import (
    Arguments as ModelArguments,
    Parameter as ModelParameter,
)
from hera.workflows.parameter import Parameter


@pytest.mark.parametrize(
    "arguments,expected_built_arguments",
    (
        pytest.param(
            Parameter(name="param-name", value="a-value"),
            ModelArguments(
                parameters=[
                    ModelParameter(
                        name="param-name",
                        value="a-value",
                    )
                ],
            ),
            id="single-param",
        ),
        pytest.param(
            [Parameter(name="param-name-1", value="a-value"), Parameter(name="param-name-2", value="a-value")],
            ModelArguments(
                parameters=[
                    ModelParameter(
                        name="param-name-1",
                        value="a-value",
                    ),
                    ModelParameter(
                        name="param-name-2",
                        value="a-value",
                    ),
                ],
            ),
            id="list-params",
        ),
        pytest.param(
            {"a-key": "a-value"},
            ModelArguments(
                parameters=[
                    ModelParameter(
                        name="a-key",
                        value="a-value",
                    )
                ],
            ),
            id="key-value-dict",
        ),
        pytest.param(
            {"a-key": Parameter(name="param-name", value="a-value")},
            ModelArguments(
                parameters=[
                    ModelParameter(
                        name="a-key",
                        value="a-value",
                    )
                ],
            ),
            id="key-param-dict",
        ),
        pytest.param(
            {"a-key": Parameter(name="a-param", value="a-value").with_name("ignore-me")},
            ModelArguments(
                parameters=[
                    ModelParameter(
                        name="a-key",
                        value="a-value",
                    )
                ],
            ),
            id="key-param-ignore-alt-name-dict",
        ),
        pytest.param(
            {"a-key": ModelParameter(name="param-name", value="a-value")},
            ModelArguments(
                parameters=[
                    ModelParameter(
                        name="a-key",
                        value="a-value",
                    )
                ],
            ),
            id="key-model-param-dict",
        ),
    ),
)
def test_argument_parameter_build(arguments, expected_built_arguments):
    assert (
        ArgumentsMixin(
            arguments=arguments,
        )._build_arguments()
        == expected_built_arguments
    )
