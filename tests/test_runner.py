"""Test the runner with local functions.

The functions should behave in the same way on the Argo cluster, meaning annotations
and import logic should be taken into account. The functions are not required to be a
part of a Workflow when running locally.
"""
import importlib
import os
from pathlib import Path
from typing import Dict, List
from unittest.mock import MagicMock, patch

import pytest

import tests.helper as test_module
from hera.shared import GlobalConfig
from hera.shared.serialization import serialize
from hera.workflows.runner import _run, _runner
from hera.workflows.script import RunnerScriptConstructor


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
            [{"name": "input-value", "value": '{"a": 3, "b": "bar"}'}],
            '{"output": [{"a": 3, "b": "bar"}]}',
        ),
    ],
)
def test_runner_parameter_inputs(
    entrypoint,
    kwargs_list: List[Dict[str, str]],
    expected_output,
    global_config_fixture: GlobalConfig,
    environ_annotations_fixture: None,
):
    # GIVEN
    global_config_fixture.experimental_features["script_annotations"] = True
    global_config_fixture.experimental_features["script_runner"] = True

    # WHEN
    output = _runner(entrypoint, kwargs_list)
    # THEN
    assert serialize(output) == expected_output


@pytest.mark.parametrize(
    "entrypoint,kwargs_list,expected_output",
    [
        (
            "tests.script_annotations.parameter_inputs:annotated_basic_types",
            [{"name": "a-but-kebab", "value": "3"}, {"name": "b-but-kebab", "value": "bar"}],
            '{"output": [{"a": 3, "b": "bar"}]}',
        ),
        (
            "tests.script_annotations.parameter_inputs:annotated_object",
            [{"name": "input-value", "value": '{"a": 3, "b": "bar"}'}],
            '{"output": [{"a": 3, "b": "bar"}]}',
        ),
        (
            "tests.script_annotations.parameter_inputs:annotated_parameter_no_name",
            [{"name": "annotated_input_value", "value": '{"a": 3, "b": "bar"}'}],
            '{"output": [{"a": 3, "b": "bar"}]}',
        ),
    ],
)
def test_runner_annotated_parameter_inputs(
    entrypoint,
    kwargs_list: List[Dict[str, str]],
    expected_output,
    global_config_fixture: GlobalConfig,
    environ_annotations_fixture: None,
):
    # GIVEN
    global_config_fixture.experimental_features["script_annotations"] = True
    global_config_fixture.experimental_features["script_runner"] = True

    # WHEN
    output = _runner(entrypoint, kwargs_list)
    # THEN
    assert serialize(output) == expected_output


@pytest.mark.parametrize(
    "function_name,kwargs_list,expected_files",
    [
        (
            "empty_str_param",
            [],
            [{"subpath": "tmp/hera/outputs/parameters/empty-str", "value": ""}],
        ),
        (
            "none_param",
            [],
            [{"subpath": "tmp/hera/outputs/parameters/null-str", "value": "null"}],
        ),
        (
            "script_param",
            [{"name": "a_number", "value": "3"}],
            [{"subpath": "tmp/hera/outputs/parameters/successor", "value": "4"}],
        ),
        (
            "script_artifact",
            [{"name": "a_number", "value": "3"}],
            [{"subpath": "tmp/hera/outputs/artifacts/successor", "value": "4"}],
        ),
        (
            "script_artifact_path",
            [{"name": "a_number", "value": "3"}],
            [{"subpath": "file.txt", "value": "4"}],
        ),
        (
            "script_artifact_and_param",
            [{"name": "a_number", "value": "3"}],
            [
                {"subpath": "tmp/hera/outputs/parameters/successor", "value": "4"},
                {"subpath": "tmp/hera/outputs/artifacts/successor", "value": "5"},
            ],
        ),
        (
            "script_two_params",
            [{"name": "a_number", "value": "3"}],
            [
                {"subpath": "tmp/hera/outputs/parameters/successor", "value": "4"},
                {"subpath": "tmp/hera/outputs/parameters/successor2", "value": "5"},
            ],
        ),
        (
            "script_two_artifacts",
            [{"name": "a_number", "value": "3"}],
            [
                {"subpath": "tmp/hera/outputs/artifacts/successor", "value": "4"},
                {"subpath": "tmp/hera/outputs/artifacts/successor2", "value": "5"},
            ],
        ),
        (
            "script_outputs_in_function_signature",
            [{"name": "a_number", "value": "3"}],
            [
                {"subpath": "tmp/hera/outputs/parameters/successor", "value": "4"},
                {"subpath": "tmp/hera/outputs/artifacts/successor2", "value": "5"},
            ],
        ),
        (
            "script_outputs_in_function_signature_with_path",
            [{"name": "a_number", "value": "3"}],
            [
                {"subpath": "successor", "value": "4"},
                {"subpath": "successor2", "value": "5"},
            ],
        ),
        (
            "script_param_artifact_in_function_signature_and_return_type",
            [{"name": "a_number", "value": "3"}],
            [
                {"subpath": "tmp/hera/outputs/parameters/successor", "value": "4"},
                {"subpath": "tmp/hera/outputs/artifacts/successor2", "value": "5"},
                {"subpath": "tmp/hera/outputs/parameters/successor3", "value": "6"},
                {"subpath": "tmp/hera/outputs/artifacts/successor4", "value": "7"},
            ],
        ),
        (
            "return_list_str",
            [],
            [{"subpath": "tmp/hera/outputs/parameters/list-of-str", "value": '["my", "list"]'}],
        ),
        (
            "return_dict",
            [],
            [{"subpath": "tmp/hera/outputs/parameters/dict-of-str", "value": '{"my-key": "my-value"}'}],
        ),
    ],
)
def test_script_annotations_outputs(
    function_name,
    kwargs_list: List[Dict[str, str]],
    expected_files: List[Dict[str, str]],
    global_config_fixture: GlobalConfig,
    environ_annotations_fixture: None,
    tmp_path: Path,
    monkeypatch,
):
    """Test that the output annotations are parsed correctly and save outputs to correct destinations."""
    for file in expected_files:
        assert not Path(tmp_path / file["subpath"]).is_file()
    # GIVEN
    global_config_fixture.experimental_features["script_annotations"] = True
    global_config_fixture.experimental_features["script_runner"] = True

    outputs_directory = str(tmp_path / "tmp/hera/outputs")
    global_config_fixture.set_class_defaults(RunnerScriptConstructor, outputs_directory=outputs_directory)

    monkeypatch.setattr(test_module, "ARTIFACT_PATH", str(tmp_path))
    os.environ["hera__outputs_directory"] = outputs_directory

    # Force a reload of the test module, as the runner performs "importlib.import_module", which
    # may fetch a cached version
    import tests.script_runner.annotated_outputs as output_tests_module

    importlib.reload(output_tests_module)

    # WHEN
    output = _runner(f"{output_tests_module.__name__}:{function_name}", kwargs_list)
    # THEN
    assert output is None, "Runner should not return values directly when using return Annotations"
    for file in expected_files:
        assert Path(tmp_path / file["subpath"]).is_file()
        assert Path(tmp_path / file["subpath"]).read_text() == file["value"]


@pytest.mark.parametrize(
    "function_name,kwargs_list,exception",
    [
        (
            "script_two_params_one_output",
            [{"name": "a_number", "value": "3"}],
            "The number of outputs does not match the annotation",
        ),
        (
            "script_param_incorrect_basic_type",
            [{"name": "a_number", "value": "3"}],
            "The type of output `successor`, `<class 'str'>` does not match the annotated type `<class 'int'>`",
        ),
        (
            "script_param_incorrect_generic_type",
            [{"name": "a_number", "value": "3"}],
            "The type of output `successor`, `<class 'int'>` does not match the annotated type `typing.Dict[str, str]`",
        ),
        (
            "script_param_no_name",
            [{"name": "a_number", "value": "3"}],
            "The name was not provided for one of the outputs.",
        ),
    ],
)
def test_script_annotations_outputs_exceptions(
    function_name,
    kwargs_list: List[Dict[str, str]],
    exception,
    global_config_fixture: GlobalConfig,
    environ_annotations_fixture: None,
):
    """Test that the output annotations throw the expected exceptions."""
    # GIVEN
    global_config_fixture.experimental_features["script_annotations"] = True
    global_config_fixture.experimental_features["script_runner"] = True

    # WHEN
    with pytest.raises(ValueError) as e:
        _ = _runner(f"tests.script_runner.annotated_outputs:{function_name}", kwargs_list)
    # THEN
    assert exception in str(e.value)


@pytest.mark.parametrize(
    "entrypoint,kwargs_list,expected_output",
    [
        (
            "tests.script_runner.annotated_outputs:script_param",
            [{"name": "a_number", "value": "3"}],
            "4",
        )
    ],
)
def test_script_annotations_outputs_no_global_config(
    entrypoint,
    kwargs_list: Dict[str, str],
    expected_output,
):
    """Test that the output annotations are ignored when global_config is not set."""
    # WHEN
    output = _runner(entrypoint, kwargs_list)

    # THEN
    assert serialize(output) == expected_output


@pytest.mark.parametrize(
    "function,file_contents,expected_output",
    [
        (
            "no_loader",
            "First test!",
            "First test!",
        ),
        (
            "json_object_loader",
            """{"a": "Hello ", "b": "there!"}""",
            "Hello there!",
        ),
        (
            "file_loader",
            "This file had a path",
            "This file had a path",
        ),
        (
            "file_loader",
            "/this/file/contains/a/path",  # A file containing a path as a string (we should not do any further processing)
            "/this/file/contains/a/path",
        ),
    ],
)
def test_script_annotations_artifact_inputs(
    function,
    file_contents,
    expected_output,
    tmp_path: Path,
    monkeypatch,
    global_config_fixture: GlobalConfig,
):
    """Test that the input artifact annotations are parsed correctly and the loaders behave as intended."""
    # GIVEN
    filepath = tmp_path / "my_file.txt"
    filepath.write_text(file_contents)

    monkeypatch.setattr(test_module, "ARTIFACT_PATH", str(filepath))

    # Force a reload of the test module, as the runner performs "importlib.import_module", which
    # may fetch a cached version
    import tests.script_runner.artifact_loaders as module

    importlib.reload(module)

    kwargs_list = []
    global_config_fixture.experimental_features["script_annotations"] = True
    os.environ["hera__script_annotations"] = ""

    # WHEN
    output = _runner(f"{module.__name__}:{function}", kwargs_list)

    # THEN
    assert serialize(output) == expected_output


@pytest.mark.parametrize(
    "entrypoint,artifact_name,file_contents,expected_output",
    [
        (
            "tests.script_runner.artifact_loaders:file_loader_default_path",
            "my-artifact",
            "Hello there!",
            "Hello there!",
        ),
    ],
)
def test_script_annotations_artifacts_no_path(
    entrypoint,
    artifact_name,
    file_contents,
    expected_output,
    tmp_path: Path,
    monkeypatch,
    global_config_fixture: GlobalConfig,
):
    """Test that the input artifact annotations are parsed correctly and the loaders behave as intended."""
    # GIVEN
    filepath = tmp_path / f"{artifact_name}"
    filepath.write_text(file_contents)

    # Trailing slash required
    monkeypatch.setattr("hera.workflows.artifact._DEFAULT_ARTIFACT_INPUT_DIRECTORY", f"{tmp_path}/")

    kwargs_list = []
    global_config_fixture.experimental_features["script_annotations"] = True
    os.environ["hera__script_annotations"] = ""

    # WHEN
    output = _runner(entrypoint, kwargs_list)

    # THEN
    assert serialize(output) == expected_output


def test_script_annotations_artifacts_wrong_loader(
    global_config_fixture: GlobalConfig,
):
    """Test that the input artifact annotation with no loader throws an exception."""
    # GIVEN
    entrypoint = "tests.script_annotations.artifact_with_invalid_loader:invalid_loader"
    kwargs_list = []
    global_config_fixture.experimental_features["script_annotations"] = True
    os.environ["hera__script_annotations"] = ""

    # WHEN
    with pytest.raises(ValueError) as e:
        _runner(entrypoint, kwargs_list)

    # THEN
    assert "value is not a valid enumeration member" in str(e.value)


@pytest.mark.parametrize(
    "kwargs_list",
    [
        [{"name": "a_string", "value": 123}],
        [{"name": "a_number", "value": 123}],
    ],
)
@patch("hera.workflows.runner._runner")
@patch("hera.workflows.runner._parse_args")
def test_run(mock_parse_args, mock_runner, kwargs_list, tmp_path: Path):
    # GIVEN
    file_path = Path(tmp_path / "test_params")
    file_path.write_text(serialize(kwargs_list))

    args = MagicMock(entrypoint="my_entrypoint", args_path=file_path)
    mock_parse_args.return_value = args
    mock_runner.return_value = kwargs_list

    # WHEN
    _run()

    # THEN
    mock_parse_args.assert_called_once()
    mock_runner.assert_called_once_with("my_entrypoint", kwargs_list)


@patch("hera.workflows.runner._runner")
@patch("hera.workflows.runner._parse_args")
def test_run_empty_file(mock_parse_args, mock_runner, tmp_path: Path):
    # GIVEN
    file_path = Path(tmp_path / "test_params")
    file_path.write_text("")

    args = MagicMock(entrypoint="my_entrypoint", args_path=file_path)
    mock_parse_args.return_value = args
    mock_runner.return_value = None

    # WHEN
    _run()

    # THEN
    mock_parse_args.assert_called_once()
    mock_runner.assert_called_once_with("my_entrypoint", [])


@patch("hera.workflows.runner._runner")
@patch("hera.workflows.runner._parse_args")
def test_run_null_string(mock_parse_args, mock_runner, tmp_path: Path):
    # GIVEN
    file_path = Path(tmp_path / "test_params")
    file_path.write_text("null")

    args = MagicMock(entrypoint="my_entrypoint", args_path=file_path)
    mock_parse_args.return_value = args
    mock_runner.return_value = None

    # WHEN
    _run()

    # THEN
    mock_parse_args.assert_called_once()
    mock_runner.assert_called_once_with("my_entrypoint", [])
