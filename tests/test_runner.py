"""Test the runner with local functions.

The functions should behave in the same way on the Argo cluster, meaning annotations
and import logic should be taken into account. The functions are not required to be a
part of a Workflow when running locally.

The tests will usually need to set the experimental feature environment variables which
can be done through monkeypatch.setenv. This is because the runner code acts as if it
is running on Argo, where the global_config will not contain the experimental features.
"""

import importlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Literal
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

import tests.helper as test_module
from hera.shared._pydantic import _PYDANTIC_VERSION
from hera.shared.serialization import serialize
from hera.workflows._runner.util import _run, _runner
from hera.workflows.io.v1 import Output


@pytest.mark.parametrize(
    "entrypoint,kwargs_list,expected_output",
    (
        pytest.param(
            "tests.script_runner.parameter_inputs:no_type_parameter",
            [{"name": "my_anything", "value": "test"}],
            "test",
            id="no-type-string",
        ),
        pytest.param(
            "tests.script_runner.parameter_inputs:no_type_parameter",
            [{"name": "my_anything", "value": "1"}],
            1,
            id="no-type-int",
        ),
        pytest.param(
            "tests.script_runner.parameter_inputs:no_type_parameter",
            [{"name": "my_anything", "value": "null"}],
            None,
            id="no-type-none",
        ),
        pytest.param(
            "tests.script_runner.parameter_inputs:no_type_parameter",
            [{"name": "my_anything", "value": "true"}],
            True,
            id="no-type-bool",
        ),
        pytest.param(
            "tests.script_runner.parameter_inputs:no_type_parameter",
            [{"name": "my_anything", "value": "[]"}],
            [],
            id="no-type-list",
        ),
        pytest.param(
            "tests.script_runner.parameter_inputs:no_type_parameter",
            [{"name": "my_anything", "value": "{}"}],
            {},
            id="no-type-dict",
        ),
        pytest.param(
            "tests.script_runner.parameter_inputs:str_parameter_expects_jsonstr_dict",
            [{"name": "my_json_str", "value": json.dumps({"my": "dict"})}],
            {"my": "dict"},
            id="str-json-param-as-dict",
        ),
        pytest.param(
            "tests.script_runner.parameter_inputs:str_parameter_expects_jsonstr_list",
            [{"name": "my_json_str", "value": json.dumps([{"my": "dict"}])}],
            [{"my": "dict"}],
            id="str-json-param-as-list",
        ),
        pytest.param(
            "tests.script_runner.parameter_inputs:annotated_str_parameter_expects_jsonstr_dict",
            [{"name": "my_json_str", "value": json.dumps({"my": "dict"})}],
            {"my": "dict"},
            id="str-json-annotated-param-as-dict",
        ),
    ),
)
def test_parameter_loading(
    entrypoint: str,
    kwargs_list: List[Dict[str, str]],
    expected_output: Any,
    monkeypatch: pytest.MonkeyPatch,
):
    # GIVEN
    monkeypatch.setenv("hera__script_annotations", "")

    # WHEN
    output = _runner(entrypoint, kwargs_list)

    # THEN
    assert output == expected_output


@pytest.mark.parametrize(
    "entrypoint,kwargs_list,expected_output",
    [
        (
            "examples.workflows.scripts.callable_script:my_function",
            [{"name": "input", "value": '{"a": 2, "b": "bar", "c": 42}'}],
            '{"output": [{"a": 2, "b": "bar", "c": 42}]}',
        ),
        (
            "examples.workflows.scripts.callable_script:another_function",
            [{"name": "inputs", "value": '[{"a": 2, "b": "bar", "c": 42}, {"a": 2, "b": "bar", "c": 42.0}]'}],
            '{"output": [{"a": 2, "b": "bar", "c": 42}, {"a": 2, "b": "bar", "c": 42.0}]}',
        ),
        (
            "examples.workflows.scripts.callable_script:str_function",
            [{"name": "input", "value": '{"a": 2, "b": "bar", "c": 42}'}],
            '{"output": [{"a": 2, "b": "bar", "c": 42}]}',
        ),
        (
            "examples.workflows.scripts.callable_script:function_kebab",
            [
                {"name": "a-but-kebab", "value": "3"},
                {"name": "b-but-kebab", "value": "bar"},
                {"name": "c-but-kebab", "value": "42.0"},
            ],
            '{"output": [{"a": 3, "b": "bar", "c": 42.0}]}',
        ),
        (
            "examples.workflows.scripts.callable_script:function_kebab_object",
            [{"name": "input-value", "value": '{"a": 3, "b": "bar", "c": "abc"}'}],
            '{"output": [{"a": 3, "b": "bar", "c": "abc"}]}',
        ),
    ],
)
def test_runner_parameter_inputs(
    entrypoint,
    kwargs_list: List[Dict[str, str]],
    expected_output,
    monkeypatch: pytest.MonkeyPatch,
):
    # GIVEN
    monkeypatch.setenv("hera__script_annotations", "")

    # WHEN
    output = _runner(entrypoint, kwargs_list)
    # THEN
    assert serialize(output) == expected_output


@pytest.mark.parametrize(
    "entrypoint,kwargs_list,expected_output,pydantic_mode",
    [
        pytest.param(
            "tests.script_runner.parameter_inputs:annotated_basic_types",
            [{"name": "a-but-kebab", "value": "3"}, {"name": "b-but-kebab", "value": "bar"}],
            '{"output": [{"a": 3, "b": "bar"}]}',
            _PYDANTIC_VERSION,
            id="basic-test",
        ),
        pytest.param(
            "tests.script_runner.parameter_inputs:annotated_basic_types",
            [{"name": "a-but-kebab", "value": "3"}, {"name": "b-but-kebab", "value": "1"}],
            '{"output": [{"a": 3, "b": "1"}]}',
            _PYDANTIC_VERSION,
            id="str-param-given-int",
        ),
        pytest.param(
            "tests.script_runner.parameter_inputs:annotated_basic_types_with_other_metadata",
            [{"name": "a-but-kebab", "value": "3"}, {"name": "b-but-kebab", "value": "1"}],
            '{"output": [{"a": 3, "b": "1"}]}',
            _PYDANTIC_VERSION,
            id="str-param-given-int",
        ),
        pytest.param(
            "tests.script_runner.parameter_inputs:annotated_object",
            [{"name": "input-value", "value": '{"a": 3, "b": "bar"}'}],
            '{"output": [{"a": 3, "b": "bar"}]}',
            _PYDANTIC_VERSION,
            id="annotated-object",
        ),
        pytest.param(
            "tests.script_runner.parameter_inputs:annotated_object_v1",
            [{"name": "input-value", "value": '{"a": 3, "b": "bar"}'}],
            '{"output": [{"a": 3, "b": "bar"}]}',
            1,
            id="annotated-object-v1",
        ),
        pytest.param(
            "tests.script_runner.parameter_inputs:annotated_parameter_no_name",
            [{"name": "annotated_input_value", "value": '{"a": 3, "b": "bar"}'}],
            '{"output": [{"a": 3, "b": "bar"}]}',
            _PYDANTIC_VERSION,
            id="annotated-param-no-name",
        ),
    ],
)
def test_runner_annotated_parameter_inputs(
    entrypoint: str,
    kwargs_list: List[Dict[str, str]],
    expected_output: Any,
    pydantic_mode: Literal[1, 2],
    monkeypatch: pytest.MonkeyPatch,
):
    # GIVEN
    monkeypatch.setenv("hera__script_annotations", "")
    monkeypatch.setenv("hera__pydantic_mode", str(pydantic_mode))
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
            [{"subpath": "tmp/hera-outputs/parameters/empty-str", "value": ""}],
        ),
        (
            "none_param",
            [],
            [{"subpath": "tmp/hera-outputs/parameters/null-str", "value": "null"}],
        ),
        (
            "script_param",
            [{"name": "a_number", "value": "3"}],
            [{"subpath": "tmp/hera-outputs/parameters/successor", "value": "4"}],
        ),
        (
            "script_artifact",
            [{"name": "a_number", "value": "3"}],
            [{"subpath": "tmp/hera-outputs/artifacts/successor", "value": "4"}],
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
                {"subpath": "tmp/hera-outputs/parameters/successor", "value": "4"},
                {"subpath": "tmp/hera-outputs/artifacts/successor", "value": "5"},
            ],
        ),
        (
            "script_two_params",
            [{"name": "a_number", "value": "3"}],
            [
                {"subpath": "tmp/hera-outputs/parameters/successor", "value": "4"},
                {"subpath": "tmp/hera-outputs/parameters/successor2", "value": "5"},
            ],
        ),
        (
            "script_two_artifacts",
            [{"name": "a_number", "value": "3"}],
            [
                {"subpath": "tmp/hera-outputs/artifacts/successor", "value": "4"},
                {"subpath": "tmp/hera-outputs/artifacts/successor2", "value": "5"},
            ],
        ),
        (
            "script_outputs_in_function_signature",
            [{"name": "a_number", "value": "3"}],
            [
                {"subpath": "tmp/hera-outputs/parameters/successor", "value": "4"},
                {"subpath": "tmp/hera-outputs/artifacts/successor2", "value": "5"},
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
                {"subpath": "tmp/hera-outputs/parameters/successor", "value": "4"},
                {"subpath": "tmp/hera-outputs/artifacts/successor2", "value": "5"},
                {"subpath": "tmp/hera-outputs/parameters/successor3", "value": "6"},
                {"subpath": "tmp/hera-outputs/artifacts/successor4", "value": "7"},
            ],
        ),
        (
            "return_list_str",
            [],
            [{"subpath": "tmp/hera-outputs/parameters/list-of-str", "value": '["my", "list"]'}],
        ),
        (
            "return_dict",
            [],
            [{"subpath": "tmp/hera-outputs/parameters/dict-of-str", "value": '{"my-key": "my-value"}'}],
        ),
    ],
)
def test_script_annotations_outputs(
    function_name,
    kwargs_list: List[Dict[str, str]],
    expected_files: List[Dict[str, str]],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that the output annotations are parsed correctly and save outputs to correct destinations."""
    # GIVEN
    monkeypatch.setenv("hera__script_annotations", "")

    outputs_directory = str(tmp_path / "tmp/hera-outputs")

    monkeypatch.setattr(test_module, "ARTIFACT_PATH", str(tmp_path))
    monkeypatch.setenv("hera__outputs_directory", outputs_directory)

    # Force a reload of the test module, as the runner performs "importlib.import_module", which
    # may fetch a cached version which will not have the correct ARTIFACT_PATH
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
    "function_name,expected_error,expected_files",
    [
        (
            "script_param_output_raises_index_error",
            IndexError,
            [{"subpath": "tmp/hera-outputs/parameters/param-output", "value": ""}],
        ),
        (
            "script_artifact_output_raises_index_error",
            IndexError,
            [{"subpath": "tmp/hera-outputs/artifacts/artifact-output", "value": ""}],
        ),
    ],
)
def test_script_raising_error_still_outputs(
    function_name,
    expected_error: type,
    expected_files: List[Dict[str, str]],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that the output annotations are parsed correctly and save outputs to correct destinations."""
    # GIVEN
    monkeypatch.setenv("hera__script_annotations", "")

    outputs_directory = str(tmp_path / "tmp/hera-outputs")

    monkeypatch.setattr(test_module, "ARTIFACT_PATH", str(tmp_path))
    monkeypatch.setenv("hera__outputs_directory", outputs_directory)

    # Force a reload of the test module, as the runner performs "importlib.import_module", which
    # may fetch a cached version which will not have the correct ARTIFACT_PATH
    import tests.script_runner.annotated_outputs as output_tests_module

    importlib.reload(output_tests_module)

    # WHEN
    with pytest.raises(expected_error):
        _runner(f"{output_tests_module.__name__}:{function_name}", [])

    # THEN
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
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that the output annotations throw the expected exceptions."""
    # GIVEN
    monkeypatch.setenv("hera__script_annotations", "")

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
            "no_loader_as_string",
            "Another test",
            "Another test",
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
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that the input artifact annotations are parsed correctly and the loaders behave as intended."""
    # GIVEN
    filepath = tmp_path / "my_file.txt"
    filepath.write_text(file_contents)

    monkeypatch.setattr(test_module, "ARTIFACT_PATH", str(filepath))

    # Force a reload of the test module, as the runner performs "importlib.import_module", which
    # may fetch a cached version which will not have the correct ARTIFACT_PATH
    import tests.script_runner.artifact_loaders as module

    importlib.reload(module)

    kwargs_list = []
    monkeypatch.setenv("hera__script_annotations", "")

    # WHEN
    output = _runner(f"{module.__name__}:{function}", kwargs_list)

    # THEN
    assert serialize(output) == expected_output


def test_script_annotations_artifact_input_loader_error(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that the input artifact loaded with wrong type throws the expected exception."""
    # GIVEN
    function_name = "no_loader_invalid_type"
    kwargs_list = []
    monkeypatch.setenv("hera__script_annotations", "")

    # Force a reload of the test module, as the runner performs "importlib.import_module", which
    # may fetch a cached version which will not have the correct ARTIFACT_PATH
    import tests.script_runner.artifact_loaders as module

    importlib.reload(module)

    # THEN
    with pytest.raises(ValidationError):
        _ = _runner(f"{module.__name__}:{function_name}", kwargs_list)


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
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that the input artifact annotations are parsed correctly and the loaders behave as intended."""
    # GIVEN
    filepath = tmp_path / f"{artifact_name}"
    filepath.write_text(file_contents)

    # Trailing slash required
    monkeypatch.setattr("hera.workflows.artifact._DEFAULT_ARTIFACT_INPUT_DIRECTORY", f"{tmp_path}/")

    kwargs_list = []
    monkeypatch.setenv("hera__script_annotations", "")

    # WHEN
    output = _runner(entrypoint, kwargs_list)

    # THEN
    assert serialize(output) == expected_output


def test_script_annotations_artifacts_wrong_loader(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test that the input artifact annotation with no loader throws an exception."""
    # GIVEN
    entrypoint = "tests.script_runner.artifact_with_invalid_loader:invalid_loader"
    kwargs_list = []
    monkeypatch.setenv("hera__script_annotations", "")

    # WHEN
    with pytest.raises(ValueError) as e:
        _runner(entrypoint, kwargs_list)

    # THEN
    assert "value is not a valid enumeration member" in str(e.value)


def test_script_annotations_unknown_type(
    monkeypatch: pytest.MonkeyPatch,
):
    # GIVEN
    expected_output = "a string"
    entrypoint = "tests.script_runner.unknown_annotation_types:unknown_annotations_ignored"
    kwargs_list = [{"name": "my_string", "value": expected_output}]
    monkeypatch.setenv("hera__script_annotations", "")

    # WHEN
    output = _runner(entrypoint, kwargs_list)

    # THEN
    assert serialize(output) == expected_output


@pytest.mark.parametrize(
    "kwargs_list",
    [
        [{"name": "a_string", "value": "123"}],
        [{"name": "a_number", "value": "123"}],
    ],
)
@patch("hera.workflows._runner.util._runner")
@patch("hera.workflows._runner.util._parse_args")
def test_run(mock_parse_args, mock_runner, kwargs_list: List[Dict[str, str]], tmp_path: Path):
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


@patch("hera.workflows._runner.util._runner")
@patch("hera.workflows._runner.util._parse_args")
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


@patch("hera.workflows._runner.util._runner")
@patch("hera.workflows._runner.util._parse_args")
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


@pytest.mark.parametrize("pydantic_mode", [1, _PYDANTIC_VERSION])
@pytest.mark.parametrize(
    "entrypoint,kwargs_list,expected_output",
    [
        pytest.param(
            "tests.script_runner.pydantic_io_vX:pydantic_input_parameters",
            [
                {"name": "my_required_int", "value": "4"},
                {"name": "my_int", "value": "3"},
                {"name": "another-int", "value": "2"},
                {"name": "multiple-ints", "value": "[1, 2, 3]"},
            ],
            "42",
            id="test parameter only input variations",
        ),
        pytest.param(
            "tests.script_runner.pydantic_io_vX:pydantic_io_in_generic",
            [
                {"name": "my_inputs", "value": '[{"my_required_int": 2, "my_annotated_int": 3}]'},
            ],
            "1",
            id="test generic usage (reverts to regular pydantic class implementation)",
        ),
    ],
)
def test_runner_pydantic_inputs_params(
    entrypoint,
    kwargs_list: List[Dict[str, str]],
    expected_output,
    pydantic_mode,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    # GIVEN
    entrypoint = entrypoint.replace("pydantic_io_vX", f"pydantic_io_v{pydantic_mode}")
    monkeypatch.setenv("hera__pydantic_mode", str(pydantic_mode))
    monkeypatch.setenv("hera__script_annotations", "")
    monkeypatch.setenv("hera__script_pydantic_io", "")

    # WHEN
    output = _runner(entrypoint, kwargs_list)

    # THEN
    assert serialize(output) == expected_output


@pytest.mark.parametrize(
    "entrypoint,expected_files,pydantic_mode",
    [
        pytest.param(
            "tests.script_runner.pydantic_io_v1:pydantic_output_parameters",
            [
                {"subpath": "tmp/hera-outputs/parameters/my_output_str", "value": "a string!"},
                {"subpath": "tmp/hera-outputs/parameters/second-output", "value": "my-val"},
            ],
            1,
            id="pydantic output parameter variations",
        ),
    ],
)
def test_runner_pydantic_output_params(
    entrypoint,
    expected_files,
    pydantic_mode,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    # GIVEN
    monkeypatch.setenv("hera__pydantic_mode", str(pydantic_mode))
    monkeypatch.setenv("hera__script_annotations", "")
    monkeypatch.setenv("hera__script_pydantic_io", "")

    import tests.script_runner.pydantic_io_v1 as module

    importlib.reload(module)

    outputs_directory = str(tmp_path / "tmp/hera-outputs")
    monkeypatch.setenv("hera__outputs_directory", outputs_directory)

    # WHEN
    output = _runner(entrypoint, [])

    # THEN
    assert isinstance(output, Output)
    for file in expected_files:
        assert Path(tmp_path / file["subpath"]).is_file()
        assert Path(tmp_path / file["subpath"]).read_text() == file["value"]


@pytest.mark.parametrize(
    "entrypoint,input_files,expected_output,pydantic_mode",
    [
        pytest.param(
            "tests.script_runner.pydantic_io_v1:pydantic_input_artifact",
            {
                "json": '{"a": 3, "b": "bar"}',
                "path": "dummy",
                "str-path": "dummy",
                "file": "dummy",
            },
            '{"a": 3, "b": "bar"}',
            1,
            id="pydantic io artifact input variations",
        ),
    ],
)
def test_runner_pydantic_input_artifacts(
    entrypoint,
    input_files: Dict,
    expected_output,
    pydantic_mode,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    # GIVEN
    for file, contents in input_files.items():
        filepath = tmp_path / file
        filepath.write_text(contents)

    monkeypatch.setattr(test_module, "ARTIFACT_PATH", str(tmp_path))

    monkeypatch.setenv("hera__pydantic_mode", str(pydantic_mode))
    monkeypatch.setenv("hera__script_annotations", "")
    monkeypatch.setenv("hera__script_pydantic_io", "")

    import tests.script_runner.pydantic_io_v1 as module

    importlib.reload(module)

    # WHEN
    output = _runner(entrypoint, [])

    # THEN
    assert serialize(output) == expected_output


@pytest.mark.parametrize(
    "entrypoint,input_files,expected_files,pydantic_mode",
    [
        pytest.param(
            "tests.script_runner.pydantic_io_v1:pydantic_output_artifact",
            {
                "json": '{"a": 3, "b": "bar"}',
                "path": "dummy",
                "str-path": "dummy",
                "file": "dummy",
            },
            [
                {"subpath": "tmp/hera-outputs/artifacts/artifact-str-output", "value": "test"},
            ],
            1,
            id="pydantic io artifact output variations",
        ),
    ],
)
def test_runner_pydantic_output_artifacts(
    entrypoint,
    input_files: Dict,
    expected_files,
    pydantic_mode,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    # GIVEN
    for file, contents in input_files.items():
        filepath = tmp_path / file
        filepath.write_text(contents)

    monkeypatch.setattr(test_module, "ARTIFACT_PATH", str(tmp_path))

    monkeypatch.setenv("hera__pydantic_mode", str(pydantic_mode))
    monkeypatch.setenv("hera__script_annotations", "")
    monkeypatch.setenv("hera__script_pydantic_io", "")

    import tests.script_runner.pydantic_io_v1 as module

    importlib.reload(module)

    outputs_directory = str(tmp_path / "tmp/hera-outputs")
    monkeypatch.setenv("hera__outputs_directory", outputs_directory)

    # WHEN
    output = _runner(entrypoint, [])

    # THEN
    assert isinstance(output, Output)
    for file in expected_files:
        assert Path(tmp_path / file["subpath"]).is_file()
        assert Path(tmp_path / file["subpath"]).read_text() == file["value"]


@pytest.mark.parametrize(
    "entrypoint,expected_files,pydantic_mode",
    [
        pytest.param(
            "tests.script_runner.pydantic_io_v1:pydantic_output_using_exit_code",
            [
                {"subpath": "tmp/hera-outputs/parameters/my_output_str", "value": "a string!"},
                {"subpath": "tmp/hera-outputs/parameters/second-output", "value": "my-val"},
            ],
            1,
            id="pydantic output with exit code",
        ),
    ],
)
def test_runner_pydantic_output_with_exit_code(
    entrypoint,
    expected_files,
    pydantic_mode,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    # GIVEN
    monkeypatch.setenv("hera__pydantic_mode", str(pydantic_mode))
    monkeypatch.setenv("hera__script_annotations", "")
    monkeypatch.setenv("hera__script_pydantic_io", "")

    import tests.script_runner.pydantic_io_v1 as module

    importlib.reload(module)

    outputs_directory = str(tmp_path / "tmp/hera-outputs")
    monkeypatch.setenv("hera__outputs_directory", outputs_directory)

    # WHEN / THEN
    output = _runner(entrypoint, [])

    assert output.exit_code == 42

    for file in expected_files:
        assert Path(tmp_path / file["subpath"]).is_file()
        assert Path(tmp_path / file["subpath"]).read_text() == file["value"]


@pytest.mark.parametrize(
    "entrypoint,expected_files,pydantic_mode",
    [
        pytest.param(
            "tests.script_runner.pydantic_io_v1:pydantic_output_using_exit_code",
            [
                {"subpath": "tmp/hera-outputs/parameters/my_output_str", "value": "a string!"},
                {"subpath": "tmp/hera-outputs/parameters/second-output", "value": "my-val"},
            ],
            1,
            id="use _run to check actual system exit",
        ),
    ],
)
@patch("hera.workflows._runner.util._parse_args")
def test_run_pydantic_output_with_exit_code(
    mock_parse_args,
    entrypoint,
    expected_files,
    pydantic_mode,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    # GIVEN
    file_path = Path(tmp_path / "test_params")
    file_path.write_text("")
    args = MagicMock(entrypoint=entrypoint, args_path=file_path)
    mock_parse_args.return_value = args

    monkeypatch.setenv("hera__pydantic_mode", str(pydantic_mode))
    monkeypatch.setenv("hera__script_annotations", "")
    monkeypatch.setenv("hera__script_pydantic_io", "")

    import tests.script_runner.pydantic_io_v1 as module

    importlib.reload(module)

    outputs_directory = str(tmp_path / "tmp/hera-outputs")
    monkeypatch.setenv("hera__outputs_directory", outputs_directory)

    # WHEN / THEN
    with pytest.raises(SystemExit) as e:
        _run()

    assert e.value.code == 42
    mock_parse_args.assert_called_once()

    for file in expected_files:
        assert Path(tmp_path / file["subpath"]).is_file()
        assert Path(tmp_path / file["subpath"]).read_text() == file["value"]


@pytest.mark.parametrize(
    "entrypoint,expected_files,expected_result,pydantic_mode",
    [
        pytest.param(
            "tests.script_runner.pydantic_io_v1:pydantic_output_using_result",
            [
                {"subpath": "tmp/hera-outputs/parameters/my_output_str", "value": "a string!"},
                {"subpath": "tmp/hera-outputs/parameters/second-output", "value": "my-val"},
            ],
            "42",
            1,
            id="pydantic output with result output",
        ),
    ],
)
def test_runner_pydantic_output_with_result(
    entrypoint,
    expected_files,
    expected_result,
    pydantic_mode,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    # GIVEN
    monkeypatch.setenv("hera__pydantic_mode", str(pydantic_mode))
    monkeypatch.setenv("hera__script_annotations", "")
    monkeypatch.setenv("hera__script_pydantic_io", "")

    outputs_directory = str(tmp_path / "tmp/hera-outputs")
    monkeypatch.setenv("hera__outputs_directory", outputs_directory)

    # WHEN / THEN
    output = _runner(entrypoint, [])

    assert serialize(output.result) == serialize(expected_result)

    for file in expected_files:
        assert Path(tmp_path / file["subpath"]).is_file()
        assert Path(tmp_path / file["subpath"]).read_text() == file["value"]


@pytest.mark.parametrize("pydantic_mode", [1, _PYDANTIC_VERSION])
@pytest.mark.parametrize(
    "entrypoint,error_type,error_match",
    [
        pytest.param(
            "tests.script_runner.pydantic_io_v2_invalid:pydantic_input_invalid",
            ValueError,
            "Annotation should have one or zero artifact and parameter annotation.",
            id="invalid input annotation",
        ),
        pytest.param(
            "tests.script_runner.pydantic_io_v2_invalid:pydantic_output_invalid",
            ValueError,
            "Annotation should have one or zero artifact and parameter annotation.",
            id="invalid output annotation",
        ),
    ],
)
def test_runner_pydantic_with_invalid_annotations(
    entrypoint,
    error_type,
    error_match,
    pydantic_mode,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    # GIVEN
    monkeypatch.setenv("hera__pydantic_mode", str(pydantic_mode))
    monkeypatch.setenv("hera__script_annotations", "")
    monkeypatch.setenv("hera__script_pydantic_io", "")

    outputs_directory = str(tmp_path / "tmp/hera-outputs")
    monkeypatch.setenv("hera__outputs_directory", outputs_directory)

    # WHEN / THEN
    with pytest.raises(error_type, match=error_match):
        _runner(entrypoint, [])


@pytest.mark.parametrize(
    "entrypoint",
    [
        "tests.script_runner.parameter_with_complex_types:optional_str_parameter",
        "tests.script_runner.parameter_with_complex_types:optional_str_parameter_using_union",
    ]
    + (
        # Union types using OR operator are allowed since python 3.10.
        [
            "tests.script_runner.parameter_with_complex_types:optional_str_parameter_using_or",
            "tests.script_runner.parameter_with_complex_types:optional_str_parameter_using_multiple_or",
        ]
        if sys.version_info[0] >= 3 and sys.version_info[1] >= 10
        else []
    ),
)
@pytest.mark.parametrize(
    "kwargs_list,expected_output",
    [
        pytest.param(
            [{"name": "my_string", "value": "a string"}],
            "a string",
        ),
        pytest.param(
            [{"name": "my_string", "value": None}],
            "null",
        ),
    ],
)
def test_script_optional_parameter(
    monkeypatch: pytest.MonkeyPatch,
    entrypoint,
    kwargs_list,
    expected_output,
):
    # GIVEN
    monkeypatch.setenv("hera__script_annotations", "")

    # WHEN
    output = _runner(entrypoint, kwargs_list)

    # THEN
    assert serialize(output) == expected_output


@pytest.mark.parametrize(
    "entrypoint,kwargs_list,expected_output",
    [
        [
            "tests.script_runner.parameter_with_complex_types:optional_int_parameter",
            [{"name": "my_int", "value": 123}],
            "123",
        ],
        [
            "tests.script_runner.parameter_with_complex_types:optional_int_parameter",
            [{"name": "my_int", "value": None}],
            "null",
        ],
        [
            "tests.script_runner.parameter_with_complex_types:union_parameter",
            [{"name": "my_param", "value": "a string"}],
            "a string",
        ],
        [
            "tests.script_runner.parameter_with_complex_types:union_parameter",
            [{"name": "my_param", "value": 123}],
            "123",
        ],
    ],
)
def test_script_with_complex_types(
    monkeypatch: pytest.MonkeyPatch,
    entrypoint,
    kwargs_list,
    expected_output,
):
    # GIVEN
    monkeypatch.setenv("hera__script_annotations", "")

    # WHEN
    output = _runner(entrypoint, kwargs_list)

    # THEN
    assert serialize(output) == expected_output
