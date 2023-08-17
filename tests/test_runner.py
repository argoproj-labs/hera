import importlib
import os
from pathlib import Path

import pytest
import tests.helper as test_module
from unittest.mock import patch

from hera.shared.serialization import serialize
from hera.workflows.script import RunnerScriptConstructor
from hera.workflows.runner import _runner


@pytest.mark.parametrize(
    "entrypoint,kwargs_list,expected_output",
    [
        (
            "examples.workflows.callable_script:my_function",
            [{"name": "input", "value": '{"a": 2, "b": "bar"}'}],
            '{"output": [{"a": 2, "b": "bar"}]}',
        ),
        (
            "examples.workflows.callable_script:another_function",
            [{"name": "inputs", "value": '[{"a": 2, "b": "bar"}, {"a": 2, "b": "bar"}]'}],
            '{"output": [{"a": 2, "b": "bar"}, {"a": 2, "b": "bar"}]}',
        ),
        (
            "examples.workflows.callable_script:str_function",
            [{"name": "input", "value": '{"a": 2, "b": "bar"}'}],
            '{"output": [{"a": 2, "b": "bar"}]}',
        ),
        (
            "examples.workflows.callable_script:function_kebab",
            [{"name": "a-but-kebab", "value": "3"}, {"name": "b-but-kebab", "value": "bar"}],
            '{"output": [{"a": 3, "b": "bar"}]}',
        ),
        (
            "examples.workflows.callable_script:function_kebab_object",
            [{"name": "input-values", "value": '{"a": 3, "b": "bar"}'}],
            '{"output": [{"a": 3, "b": "bar"}]}',
        ),
    ],
)
def test(entrypoint, kwargs_list, expected_output, global_config_fixture, environ_annotations_fixture):
    # GIVEN
    global_config_fixture.experimental_features["script_annotations"] = True
    global_config_fixture.experimental_features["script_runner"] = True

    # WHEN
    output = _runner(entrypoint, kwargs_list)
    # THEN
    assert serialize(output) == expected_output


@pytest.mark.parametrize(
    "entrypoint,kwargs_list,expected_files",
    [
        (
            "tests.script_annotations_outputs.script_annotations_output:script_param",
            [{"name": "a_number", "value": "3"}],
            [{"path": "hera/outputs/parameters/successor", "value": "4"}],
        ),
        (
            "tests.script_annotations_outputs.script_annotations_output:script_artifact",
            [{"name": "a_number", "value": "3"}],
            [{"path": "hera/outputs/artifacts/successor", "value": "4"}],
        ),
        (
            "tests.script_annotations_outputs.script_annotations_output:script_artifact_path",
            [{"name": "a_number", "value": "3"}],
            [{"path": "file.txt", "value": "4"}],
        ),
        (
            "tests.script_annotations_outputs.script_annotations_output:script_artifact_and_param",
            [{"name": "a_number", "value": "3"}],
            [
                {"path": "hera/outputs/parameters/successor", "value": "4"},
                {"path": "hera/outputs/artifacts/successor", "value": "5"},
            ],
        ),
        (
            "tests.script_annotations_outputs.script_annotations_output:script_two_params",
            [{"name": "a_number", "value": "3"}],
            [
                {"path": "hera/outputs/parameters/successor", "value": "4"},
                {"path": "hera/outputs/parameters/successor2", "value": "5"},
            ],
        ),
        (
            "tests.script_annotations_outputs.script_annotations_output:script_two_artifacts",
            [{"name": "a_number", "value": "3"}],
            [
                {"path": "hera/outputs/artifacts/successor", "value": "4"},
                {"path": "hera/outputs/artifacts/successor2", "value": "5"},
            ],
        ),
    ],
)
# @patch("hera.workflows.runner.importlib")
def test_script_annotations_outputs(
    # mock_importlib,
    entrypoint,
    kwargs_list,
    expected_files,
    global_config_fixture,
    environ_annotations_fixture,
    tmp_path_fixture,
    # tmp_path,
    monkeypatch,
):
    """Test that the output annotations are parsed correctly and save outputs to correct destinations."""

    # GIVEN
    global_config_fixture.experimental_features["script_annotations"] = True
    global_config_fixture.experimental_features["script_runner"] = True

    monkeypatch.setattr(test_module, "ARTIFACT_PATH", str(tmp_path_fixture))
    os.environ["hera__outputs_directory"] = str(tmp_path_fixture / "hera/outputs")

    # WHEN
    output = _runner(entrypoint, kwargs_list)
    # THEN
    assert serialize(output) == "null"
    for file in expected_files:
        assert Path(tmp_path_fixture / file["path"]).is_file()
        assert Path(tmp_path_fixture / file["path"]).read_text() == file["value"]


@pytest.mark.parametrize(
    "entrypoint,kwargs_list,exception",
    [
        (
            "tests.script_annotations_outputs.script_annotations_output:script_two_params_one_output",
            [{"name": "a_number", "value": "3"}],
            "The number of outputs does not match the annotation",
        ),
        (
            "tests.script_annotations_outputs.script_annotations_output:script_param_incorrect_type",
            [{"name": "a_number", "value": "3"}],
            "The type of output `successor`, `<class 'str'>` does not match the annotated type `<class 'int'>`",
        ),
        (
            "tests.script_annotations_outputs.script_annotations_output:script_param_no_name",
            [{"name": "a_number", "value": "3"}],
            "The name was not provided for one of the outputs.",
        ),
    ],
)
def test_script_annotations_outputs_exceptions(
    entrypoint, kwargs_list, exception, global_config_fixture, environ_annotations_fixture
):
    """Test that the output annotations throw the expected exceptions."""

    # GIVEN
    global_config_fixture.experimental_features["script_annotations"] = True
    global_config_fixture.experimental_features["script_runner"] = True

    # WHEN
    with pytest.raises(ValueError) as e:
        _ = _runner(entrypoint, kwargs_list)
    # THEN
    assert exception in str(e.value)


@pytest.mark.parametrize(
    "entrypoint,kwargs_list,expected_output",
    [
        (
            "tests.script_annotations_outputs.script_annotations_output:script_param",
            [{"name": "a_number", "value": "3"}],
            "4",
        )
    ],
)
def test_script_annotations_outputs_no_global_config(entrypoint, kwargs_list, expected_output):
    """Test that the output annotations are ignored when global_config is not set."""

    # WHEN
    output = _runner(entrypoint, kwargs_list)

    # THEN
    assert serialize(output) == expected_output


@pytest.mark.parametrize(
    "entrypoint,file_contents,expected_output",
    [
        (
            "tests.script_annotations_artifacts.script_annotations_artifact_path:read_artifact",
            "Hello there!",
            "Hello there!",
        ),
        (
            "tests.script_annotations_artifacts.script_annotations_artifact_object:read_artifact",
            """{"a": "Hello ", "b": "there!"}""",
            "Hello there!",
        ),
        (
            "tests.script_annotations_artifacts.script_annotations_artifact_file:read_artifact",
            "Hello there!",
            "Hello there!",
        ),
        (
            "tests.script_annotations_artifacts.script_annotations_artifact_file_with_path:read_artifact",
            "/this/is/a/path",
            "/this/is/a/path",
        ),
    ],
)
def test_script_annotations_artifacts(
    entrypoint, file_contents, expected_output, tmp_path, monkeypatch, global_config_fixture
):
    """Test that the input artifact annotations are parsed correctly and the loaders behave as intended."""

    # GIVEN
    if not tmp_path.is_file():
        tmp_path = tmp_path / "my_file.txt"

    tmp_path.touch()
    tmp_path.write_text(file_contents)
    import tests.helper as test_module

    monkeypatch.setattr(test_module, "ARTIFACT_PATH", str(tmp_path))
    kwargs_list = []
    global_config_fixture.experimental_features["script_annotations"] = True
    os.environ["hera__script_annotations"] = ""

    # WHEN
    output = _runner(entrypoint, kwargs_list)

    # THEN
    assert serialize(output) == expected_output


@pytest.mark.parametrize(
    "entrypoint",
    ["tests.script_annotations_artifacts.script_annotations_artifact_wrong_loader:read_artifact"],
)
def test_script_annotations_artifacts_wrong_loader(entrypoint, global_config_fixture):
    """Test that the input artifact annotation with no loader throws an exception."""

    # GIVEN
    kwargs_list = []
    global_config_fixture.experimental_features["script_annotations"] = True
    os.environ["hera__script_annotations"] = ""

    # WHEN
    with pytest.raises(ValueError) as e:
        _runner(entrypoint, kwargs_list)

    # THEN
    assert "value is not a valid enumeration member" in str(e.value)
