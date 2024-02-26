import os
from pathlib import Path
from typing import Any, Union

import pytest

from hera.workflows._runner.script_annotations_util import (
    _get_outputs_path,
    get_annotated_artifact_value,
    get_annotated_param_value,
)
from hera.workflows.artifact import Artifact, ArtifactLoader
from hera.workflows.models import ValueFrom
from hera.workflows.parameter import Parameter


@pytest.mark.parametrize(
    "destination,expected_path",
    [
        (Parameter(name="a-param"), Path("/tmp/hera-outputs/parameters/a-param")),
        (Artifact(name="an-artifact"), Path("/tmp/hera-outputs/artifacts/an-artifact")),
        (Artifact(name="artifact-custom-path", path="/tmp/my-path"), Path("/tmp/my-path")),
    ],
)
def test_get_outputs_path(destination: Union[Parameter, Artifact], expected_path: Path):
    os.environ["hera__outputs_directory"] = "/tmp/hera-outputs"
    assert _get_outputs_path(destination) == expected_path


@pytest.mark.parametrize(
    "func_param_name,param_annotation,kwargs,expected_value",
    [
        pytest.param(
            "func_param_name_only",
            Parameter(description="use func param name"),
            {"func_param_name_only": "value"},
            "value",
            id="parameter-annotation-has-no-name",
        ),
        pytest.param(
            "dummy_name",
            Parameter(name="input-param-test"),
            {"input-param-test": "value"},
            "value",
            id="use-parameter-name",
        ),
        pytest.param(
            "func_param_name",
            Parameter(name="input-param-test"),
            {"func_param_name": "value"},
            "value",
            id="user-passes-func-param-name-instead-of-annotation",
        ),
        pytest.param(
            "dummy_name",
            Parameter(name="output-default-path-test", output=True),
            {},
            Path("/tmp/hera-outputs/parameters/output-default-path-test"),
            id="output-parameter-with-default",
        ),
        pytest.param(
            "dummy_name",
            Parameter(name="output-path-test", value_from=ValueFrom(path="/tmp/test"), output=True),
            {},
            Path("/tmp/test"),
            id="output-parameter-with-custom-path",
        ),
    ],
)
def test_get_annotated_param_value(
    func_param_name,
    param_annotation,
    kwargs,
    expected_value,
):
    assert get_annotated_param_value(func_param_name, param_annotation, kwargs) == expected_value


def test_get_annotated_param_value_error():
    with pytest.raises(RuntimeError, match="my_func_param was not given a value"):
        get_annotated_param_value("my_func_param", Parameter(), {})


def test_get_annotated_param_value_error_param_name():
    with pytest.raises(RuntimeError, match="my-func-param was not given a value"):
        get_annotated_param_value("my_func_param", Parameter(name="my-func-param"), {})


@pytest.mark.parametrize(
    "file_contents,artifact,expected_return",
    [
        pytest.param('{"json": "object"}', Artifact(loader=ArtifactLoader.json), {"json": "object"}, id="json-load"),
        pytest.param('{"json": "object"}', Artifact(loader=ArtifactLoader.file), '{"json": "object"}', id="file-load"),
    ],
)
def test_get_annotated_artifact_value_json_inputs(
    file_contents: str,
    artifact: Artifact,
    expected_return: Any,
    tmp_path: Path,
):
    file_path = tmp_path / "contents.txt"
    file_path.write_text(file_contents)
    artifact.path = file_path
    assert get_annotated_artifact_value(artifact) == expected_return


@pytest.mark.parametrize(
    "file_contents,artifact",
    [
        pytest.param('{"json": "object"}', Artifact(loader=None), id="file-load"),
    ],
)
def test_get_annotated_artifact_value_path_inputs(
    file_contents: str,
    artifact: Artifact,
    tmp_path: Path,
):
    file_path = tmp_path / "contents.txt"
    file_path.write_text(file_contents)
    artifact.path = file_path
    assert get_annotated_artifact_value(artifact) == file_path


@pytest.mark.parametrize(
    "file_contents,artifact",
    [
        pytest.param('{"json": "object"}', Artifact(loader=None), id="file-load"),
    ],
)
def test_get_annotated_artifact_value_path_inputs(
    file_contents: str,
    artifact: Artifact,
    tmp_path: Path,
):
    file_path = tmp_path / "contents.txt"
    file_path.write_text(file_contents)
    artifact.path = file_path
    assert get_annotated_artifact_value(artifact) == file_path


@pytest.mark.parametrize(
    "artifact,expected_path",
    [
        pytest.param(Artifact(path="/tmp/test.txt", output=True), "/tmp/test.txt", id="given-path"),
        pytest.param(
            Artifact(name="artifact-name", output=True), "/tmp/hera-outputs/artifacts/artifact-name", id="default-path"
        ),
    ],
)
def test_get_annotated_artifact_value_path_outputs(
    artifact: Artifact,
    expected_path: str,
):
    assert get_annotated_artifact_value(artifact) == Path(expected_path)
