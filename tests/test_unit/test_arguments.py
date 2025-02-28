"""The unit tests of the Parameter class, covering the name: Optional[str] behaviour."""

import pytest

from hera.workflows._mixins import ArgumentsMixin
from hera.workflows.artifact import Artifact
from hera.workflows.models import (
    Arguments as ModelArguments,
    Artifact as ModelArtifact,
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
        pytest.param(
            {"a-key": Parameter(value="a-value")},
            ModelArguments(
                parameters=[
                    ModelParameter(
                        name="a-key",
                        value="a-value",
                    )
                ],
            ),
            id="unnamed-param",
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


model_artifact = ModelArtifact(name="artifact-name", from_="somewhere")


@pytest.mark.parametrize(
    "arguments,expected_built_arguments",
    (
        pytest.param(
            ModelArtifact(
                name="artifact-name",
                from_="somewhere",
            ),
            ModelArguments(
                artifacts=[
                    ModelArtifact(
                        name="artifact-name",
                        from_="somewhere",
                    )
                ],
            ),
            id="single-model-artifact",
        ),
        pytest.param(
            [
                ModelArtifact(
                    name="artifact-name-1",
                    from_="somewhere",
                ),
                ModelArtifact(
                    name="artifact-name-2",
                    from_="somewhere",
                ),
            ],
            ModelArguments(
                artifacts=[
                    ModelArtifact(
                        name="artifact-name-1",
                        from_="somewhere",
                    ),
                    ModelArtifact(
                        name="artifact-name-2",
                        from_="somewhere",
                    ),
                ],
            ),
            id="list-model-artifacts",
        ),
        pytest.param(
            {"a-key": ModelArtifact(name="artifact-name", from_="somewhere")},
            ModelArguments(
                artifacts=[
                    ModelArtifact(
                        name="a-key",
                        from_="somewhere",
                    )
                ],
            ),
            id="model-artifact-in-dict",
        ),
        pytest.param(
            [
                {
                    "a-key": model_artifact,
                },
                model_artifact,
            ],
            ModelArguments(
                artifacts=[
                    ModelArtifact(
                        name="a-key",
                        from_="somewhere",
                    ),
                    ModelArtifact(
                        name="artifact-name",
                        from_="somewhere",
                    ),
                ],
            ),
            id="do-not-rename-original-artifact-object",
        ),
        pytest.param(
            {"a-key": Artifact(name="artifact-name", from_="somewhere").with_name("ignore-me")},
            ModelArguments(
                artifacts=[
                    ModelArtifact(
                        name="a-key",
                        from_="somewhere",
                    )
                ],
            ),
            id="hera-artifact-ignore-alt-name",
        ),
        pytest.param(
            {"a-key": Artifact(from_="somewhere")},
            ModelArguments(
                artifacts=[
                    ModelArtifact(
                        name="a-key",
                        from_="somewhere",
                    )
                ],
            ),
            id="unnamed-artifact",
        ),
    ),
)
def test_argument_artifact_build(arguments, expected_built_arguments):
    assert (
        ArgumentsMixin(
            arguments=arguments,
        )._build_arguments()
        == expected_built_arguments
    )


@pytest.mark.parametrize(
    "arguments,expected_built_arguments",
    (
        pytest.param(
            None,
            None,
            id="no-arguments",
        ),
        pytest.param(
            ModelArguments(),
            ModelArguments(),
            id="model-arguments",
        ),
        pytest.param(
            [Parameter(name="param-name", value="a-value"), Artifact(name="artifact-name", from_="somewhere")],
            ModelArguments(
                parameters=[
                    ModelParameter(
                        name="param-name",
                        value="a-value",
                    )
                ],
                artifacts=[
                    ModelArtifact(
                        name="artifact-name",
                        from_="somewhere",
                    )
                ],
            ),
            id="mixed-list",
        ),
        pytest.param(
            {"param-name": "a-value", "a-key": ModelArtifact(name="artifact-name", from_="somewhere")},
            ModelArguments(
                parameters=[
                    ModelParameter(
                        name="param-name",
                        value="a-value",
                    )
                ],
                artifacts=[
                    ModelArtifact(
                        name="a-key",
                        from_="somewhere",
                    )
                ],
            ),
            id="mixed-dict",
        ),
        pytest.param(
            [
                {"param-name": "a-value"},
                ModelArtifact(name="artifact-name", from_="somewhere"),
            ],
            ModelArguments(
                parameters=[
                    ModelParameter(
                        name="param-name",
                        value="a-value",
                    )
                ],
                artifacts=[
                    ModelArtifact(
                        name="artifact-name",
                        from_="somewhere",
                    )
                ],
            ),
            id="param-dict-in-list",
        ),
        pytest.param(
            [
                {"param-name": "a-value"},
                {"a-key": Artifact(name="artifact-name", from_="somewhere").with_name("ignore-me")},
            ],
            ModelArguments(
                parameters=[
                    ModelParameter(
                        name="param-name",
                        value="a-value",
                    )
                ],
                artifacts=[
                    ModelArtifact(
                        name="a-key",
                        from_="somewhere",
                    )
                ],
            ),
            id="multiple-dicts-in-list",
        ),
    ),
)
def test_mixed_arguments_build(arguments, expected_built_arguments):
    assert (
        ArgumentsMixin(
            arguments=arguments,
        )._build_arguments()
        == expected_built_arguments
    )


def test_invalid_type_in_argument_list():
    with pytest.raises(TypeError):
        ArgumentsMixin.construct(
            arguments=[1],
        )._build_arguments()
