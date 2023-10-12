import os
from pathlib import Path
from typing import Dict, List, Literal
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
            [{"name": "input", "value": '{"a": 2, "b": "bar", "c": 42}'}],
            '{"output": [{"a": 2, "b": "bar", "c": 42}]}',
        ),
        (
            "examples.workflows.callable_script:another_function",
            [{"name": "inputs", "value": '[{"a": 2, "b": "bar", "c": 42}, {"a": 2, "b": "bar", "c": 42.0}]'}],
            '{"output": [{"a": 2, "b": "bar", "c": 42}, {"a": 2, "b": "bar", "c": 42.0}]}',
        ),
        (
            "examples.workflows.callable_script:str_function",
            [{"name": "input", "value": '{"a": 2, "b": "bar"}'}],
            '{"output": [{"a": 2, "b": "bar"}]}',
        ),
        (
            "examples.workflows.callable_script:function_kebab",
            [
                {"name": "a-but-kebab", "value": "3"},
                {"name": "b-but-kebab", "value": "bar"},
                {"name": "c-but-kebab", "value": "42.0"},
            ],
            '{"output": [{"a": 3, "b": "bar", "c": 42.0}]}',
        ),
        (
            "examples.workflows.callable_script:function_kebab_object",
            [{"name": "input-values", "value": '{"a": 3, "b": "bar", "c": "abc"}'}],
            '{"output": [{"a": 3, "b": "bar", "c": "abc"}]}',
        ),
    ],
)
def test(
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
    "entrypoint,kwargs_list,expected_files",
    [
        (
            "tests.script_annotations_outputs.script_annotations_output:empty_str_param",
            [],
            [{"path": "tmp/hera/outputs/parameters/empty-str", "value": ""}],
        ),
        (
            "tests.script_annotations_outputs.script_annotations_output:none_param",
            [],
            [{"path": "tmp/hera/outputs/parameters/null-str", "value": "null"}],
        ),
        (
            "tests.script_annotations_outputs.script_annotations_output:script_param",
            [{"name": "a_number", "value": "3"}],
            [{"path": "tmp/hera/outputs/parameters/successor", "value": "4"}],
        ),
        (
            "tests.script_annotations_outputs.script_annotations_output:script_artifact",
            [{"name": "a_number", "value": "3"}],
            [{"path": "tmp/hera/outputs/artifacts/successor", "value": "4"}],
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
                {"path": "tmp/hera/outputs/parameters/successor", "value": "4"},
                {"path": "tmp/hera/outputs/artifacts/successor", "value": "5"},
            ],
        ),
        (
            "tests.script_annotations_outputs.script_annotations_output:script_two_params",
            [{"name": "a_number", "value": "3"}],
            [
                {"path": "tmp/hera/outputs/parameters/successor", "value": "4"},
                {"path": "tmp/hera/outputs/parameters/successor2", "value": "5"},
            ],
        ),
        (
            "tests.script_annotations_outputs.script_annotations_output:script_two_artifacts",
            [{"name": "a_number", "value": "3"}],
            [
                {"path": "tmp/hera/outputs/artifacts/successor", "value": "4"},
                {"path": "tmp/hera/outputs/artifacts/successor2", "value": "5"},
            ],
        ),
        (
            "tests.script_annotations_outputs.script_annotations_output:script_outputs_in_function_signature",
            [{"name": "a_number", "value": "3"}],
            [
                {"path": "tmp/hera/outputs/parameters/successor", "value": "4"},
                {"path": "tmp/hera/outputs/artifacts/successor2", "value": "5"},
            ],
        ),
        (
            "tests.script_annotations_outputs.script_annotations_output:script_param_artifact_in_function_signature_and_return_type",
            [{"name": "a_number", "value": "3"}],
            [
                {"path": "tmp/hera/outputs/parameters/successor", "value": "4"},
                {"path": "tmp/hera/outputs/artifacts/successor2", "value": "5"},
                {"path": "tmp/hera/outputs/parameters/successor3", "value": "6"},
                {"path": "tmp/hera/outputs/artifacts/successor4", "value": "7"},
            ],
        ),
        (
            "tests.script_annotations_outputs.script_annotations_output:return_list_str",
            [],
            [{"path": "tmp/hera/outputs/parameters/list-of-str", "value": '["my", "list"]'}],
        ),
        (
            "tests.script_annotations_outputs.script_annotations_output:return_dict",
            [],
            [{"path": "tmp/hera/outputs/parameters/dict-of-str", "value": '{"my-key": "my-value"}'}],
        ),
    ],
)
def test_script_annotations_outputs(
    entrypoint,
    kwargs_list: List[Dict[str, str]],
    expected_files: List[Dict[str, str]],
    global_config_fixture: GlobalConfig,
    environ_annotations_fixture: None,
    tmp_path_fixture: Path,
    monkeypatch,
):
    """Test that the output annotations are parsed correctly and save outputs to correct destinations."""
    for file in expected_files:
        assert not Path(tmp_path_fixture / file["path"]).is_file()
    # GIVEN
    global_config_fixture.experimental_features["script_annotations"] = True
    global_config_fixture.experimental_features["script_runner"] = True

    outputs_directory = str(tmp_path_fixture / "tmp/hera/outputs")
    global_config_fixture.set_class_defaults(RunnerScriptConstructor, outputs_directory=outputs_directory)

    monkeypatch.setattr(test_module, "ARTIFACT_PATH", str(tmp_path_fixture))
    os.environ["hera__outputs_directory"] = outputs_directory

    # WHEN
    output = _runner(entrypoint, kwargs_list)
    # THEN
    assert output is None, "Runner should not return values directly when using return Annotations"
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
            "tests.script_annotations_outputs.script_annotations_output:script_param_incorrect_basic_type",
            [{"name": "a_number", "value": "3"}],
            "The type of output `successor`, `<class 'str'>` does not match the annotated type `<class 'int'>`",
        ),
        (
            "tests.script_annotations_outputs.script_annotations_output:script_param_incorrect_generic_type",
            [{"name": "a_number", "value": "3"}],
            "The type of output `successor`, `<class 'int'>` does not match the annotated type `typing.Dict[str, str]`",
        ),
        (
            "tests.script_annotations_outputs.script_annotations_output:script_param_no_name",
            [{"name": "a_number", "value": "3"}],
            "The name was not provided for one of the outputs.",
        ),
    ],
)
def test_script_annotations_outputs_exceptions(
    entrypoint: Literal["tests.script_annotations_outputs.script_annotation…"],
    kwargs_list: List[Dict[str, str]],
    exception: Literal[
        "The number of outputs does not match the annotatio…",
        "The type of output `successor`, `<class 'str'>` do…",
        "The name was not provided for one of the outputs.",
    ],
    global_config_fixture: GlobalConfig,
    environ_annotations_fixture: None,
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
def test_script_annotations_outputs_no_global_config(
    entrypoint: Literal["tests.script_annotations_outputs.script_annotation…"],
    kwargs_list: Dict[str, str],
    expected_output: Literal["4"],
):
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
    entrypoint: Literal["tests.script_annotations_artifacts.script_annotati…"],
    file_contents: Literal["Hello there!", '{"a": "Hello ", "b": "there!"}', "/this/is/a/path"],
    expected_output: Literal["Hello there!", "/this/is/a/path"],
    tmp_path: Path,
    monkeypatch,
    global_config_fixture: GlobalConfig,
):
    """Test that the input artifact annotations are parsed correctly and the loaders behave as intended."""
    # GIVEN
    filepath = tmp_path / "my_file.txt"

    filepath.write_text(file_contents)
    import tests.helper as test_module

    monkeypatch.setattr(test_module, "ARTIFACT_PATH", str(filepath))
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
def test_script_annotations_artifacts_wrong_loader(
    entrypoint: Literal["tests.script_annotations_artifacts.script_annotati…"], global_config_fixture: GlobalConfig
):
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
