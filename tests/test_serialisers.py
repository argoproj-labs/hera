import json
import pickle
from pathlib import Path
from typing import Any, Dict, List

import pytest
from pydantic import ValidationError as V2ValidationError
from pydantic.v1 import ValidationError as V1ValidationError

from hera.shared._pydantic import _PYDANTIC_VERSION
from hera.workflows._runner.util import _runner
from hera.workflows.io.v1 import Output as OutputV1
from hera.workflows.io.v2 import Output as OutputV2


@pytest.mark.parametrize("pydantic_mode", [1, _PYDANTIC_VERSION])
@pytest.mark.parametrize(
    "entrypoint,kwargs_list,expected_output",
    (
        pytest.param(
            "tests.script_runner.parameter_serialisers_vX:base_model_auto_load",
            [{"name": "my-parameter", "value": json.dumps({"a": "hello ", "b": "world"})}],
            "hello world",
            id="load-base-models-automatically",
        ),
        pytest.param(
            "tests.script_runner.parameter_serialisers_vX:load_typed_dict",
            [{"name": "my-parameter", "value": json.dumps({"a": "hello ", "b": "world"})}],
            "hello world",
            id="allow-non-type-checkable-types",
        ),
        pytest.param(
            "tests.script_runner.parameter_serialisers_vX:non_base_model_with_class_loader",
            [{"name": "my-parameter", "value": json.dumps({"a": "hello ", "b": "world"})}],
            "hello world",
            id="load-non-base-model-with-class-loader",
        ),
        pytest.param(
            "tests.script_runner.parameter_serialisers_vX:non_base_model_with_lambda_function_loader",
            [{"name": "my-parameter", "value": json.dumps({"a": "hello ", "b": "world"})}],
            "hello world",
            id="load-non-base-model-with-lambda-function-loader",
        ),
        pytest.param(
            "tests.script_runner.parameter_serialisers_vX:pydantic_input_with_loader_on_attribute",
            [{"name": "my-parameter", "value": json.dumps({"a": "hello ", "b": "world"})}],
            "hello world",
            id="pydantic-input-with-loader-on-attribute",
        ),
    ),
)
def test_parameter_loading(
    entrypoint: str,
    kwargs_list: List[Dict[str, str]],
    expected_output: List[Dict[str, Any]],
    pydantic_mode: int,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv("hera__pydantic_mode", str(pydantic_mode))
    monkeypatch.setenv("hera__script_pydantic_io", "")
    entrypoint = entrypoint.replace("parameter_serialisers_vX", f"parameter_serialisers_v{pydantic_mode}")

    # WHEN
    output = _runner(entrypoint, kwargs_list)

    # THEN
    assert output == expected_output


@pytest.mark.parametrize("pydantic_mode", [1, _PYDANTIC_VERSION])
def test_loading_wrong_type(
    pydantic_mode: int,
    monkeypatch: pytest.MonkeyPatch,
):
    # GIVEN
    if pydantic_mode == 1:
        error = V1ValidationError
    else:
        error = V2ValidationError

    monkeypatch.setenv("hera__pydantic_mode", str(pydantic_mode))
    monkeypatch.setenv("hera__script_pydantic_io", "")
    entrypoint = "tests.script_runner.parameter_serialisers_vX:load_wrong_type"
    entrypoint = entrypoint.replace("parameter_serialisers_vX", f"parameter_serialisers_v{pydantic_mode}")
    kwargs_list = [{"name": "my-parameter", "value": json.dumps({"a": "hello ", "b": "world"})}]

    with pytest.raises(error):
        # WHEN
        _runner(entrypoint, kwargs_list)


@pytest.mark.parametrize("pydantic_mode", [1, _PYDANTIC_VERSION])
@pytest.mark.parametrize(
    "entrypoint,kwargs_list,expected_files",
    (
        pytest.param(
            "tests.script_runner.parameter_serialisers_vX:base_model_auto_save",
            [
                {"name": "a", "value": "hello "},
                {"name": "b", "value": "world"},
            ],
            [{"subpath": "tmp/hera-outputs/parameters/my-output", "value": json.dumps({"a": "hello ", "b": "world"})}],
            id="save-base-models-automatically",
        ),
        pytest.param(
            "tests.script_runner.parameter_serialisers_vX:non_base_model_with_class_serialiser",
            [
                {"name": "a", "value": "hello "},
                {"name": "b", "value": "world"},
            ],
            [{"subpath": "tmp/hera-outputs/parameters/my-output", "value": json.dumps({"a": "hello ", "b": "world"})}],
            id="save-non-base-model-with-class-loader",
        ),
        pytest.param(
            "tests.script_runner.parameter_serialisers_vX:pydantic_output_with_dumper_on_attribute",
            [
                {"name": "a", "value": "hello "},
                {"name": "b", "value": "world"},
            ],
            [{"subpath": "tmp/hera-outputs/parameters/my-output", "value": json.dumps({"a": "hello ", "b": "world"})}],
            id="save-pydantic-output-with-custom-field-serialiser",
        ),
    ),
)
def test_parameter_dumping(
    entrypoint: str,
    kwargs_list: List[Dict[str, str]],
    expected_files: List[Dict[str, str]],
    pydantic_mode: int,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    # GIVEN
    outputs_directory = str(tmp_path / "tmp/hera-outputs")
    monkeypatch.setenv("hera__outputs_directory", outputs_directory)
    monkeypatch.setenv("hera__pydantic_mode", str(pydantic_mode))
    monkeypatch.setenv("hera__script_pydantic_io", "")
    entrypoint = entrypoint.replace("parameter_serialisers_vX", f"parameter_serialisers_v{pydantic_mode}")

    # WHEN
    output = _runner(entrypoint, kwargs_list)

    # THEN
    assert output is None or isinstance(output, (OutputV1, OutputV2)), (
        "Runner should not return values directly when using return Annotations"
    )  # (not for Output objects)
    for file in expected_files:
        assert Path(tmp_path / file["subpath"]).is_file()
        assert Path(tmp_path / file["subpath"]).read_text() == file["value"]


@pytest.mark.parametrize("pydantic_mode", [1, _PYDANTIC_VERSION])
@pytest.mark.parametrize(
    "entrypoint,artifact_name,file_contents,expected_output",
    (
        pytest.param(
            "tests.script_runner.artifact_serialisers_vX:base_model_auto_load",
            "my-artifact",
            json.dumps({"a": "hello ", "b": "world"}),
            "hello world",
            id="load-base-models-automatically",
        ),
        pytest.param(
            "tests.script_runner.artifact_serialisers_vX:non_base_model_with_class_loader",
            "my-artifact",
            json.dumps({"a": "hello ", "b": "world"}),
            "hello world",
            id="load-non-base-model-with-class-loader",
        ),
        pytest.param(
            "tests.script_runner.artifact_serialisers_vX:non_base_model_with_lambda_function_loader",
            "my-artifact",
            json.dumps({"a": "hello ", "b": "world"}),
            "hello world",
            id="load-non-base-model-with-lambda-function-loader",
        ),
        pytest.param(
            "tests.script_runner.artifact_serialisers_vX:pydantic_input_with_loader_on_attribute",
            "my-artifact",
            json.dumps({"a": "hello ", "b": "world"}),
            "hello world",
            id="pydantic-input-with-loader-on-attribute",
        ),
    ),
)
def test_artifact_loading(
    entrypoint: str,
    artifact_name: str,
    file_contents: str,
    expected_output: List[Dict[str, Any]],
    pydantic_mode: int,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    # GIVEN
    filepath = tmp_path / f"{artifact_name}"
    filepath.write_text(file_contents)

    # Trailing slash required
    monkeypatch.setattr("hera.workflows.artifact._DEFAULT_ARTIFACT_INPUT_DIRECTORY", f"{tmp_path}/")

    monkeypatch.setenv("hera__pydantic_mode", str(pydantic_mode))
    monkeypatch.setenv("hera__script_pydantic_io", "")
    entrypoint = entrypoint.replace("artifact_serialisers_vX", f"artifact_serialisers_v{pydantic_mode}")

    # WHEN
    output = _runner(entrypoint, [])

    # THEN
    assert output == expected_output


@pytest.mark.parametrize("pydantic_mode", [1, _PYDANTIC_VERSION])
@pytest.mark.parametrize(
    "entrypoint,artifact_name,file_contents,expected_output",
    (
        pytest.param(
            "tests.script_runner.artifact_serialisers_vX:bytes_loader",
            "my-artifact",
            pickle.dumps("some bytes"),
            b"some bytes",
            id="load-bytes-with-loader",
        ),
    ),
)
def test_artifact_byte_loading(
    entrypoint: str,
    artifact_name: str,
    file_contents: str,
    expected_output: List[Dict[str, Any]],
    pydantic_mode: int,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    # GIVEN
    filepath = tmp_path / f"{artifact_name}"
    filepath.write_bytes(file_contents)

    # Trailing slash required
    monkeypatch.setattr("hera.workflows.artifact._DEFAULT_ARTIFACT_INPUT_DIRECTORY", f"{tmp_path}/")

    monkeypatch.setenv("hera__pydantic_mode", str(pydantic_mode))
    monkeypatch.setenv("hera__script_pydantic_io", "")
    entrypoint = entrypoint.replace("artifact_serialisers_vX", f"artifact_serialisers_v{pydantic_mode}")

    # WHEN
    output = _runner(entrypoint, [])

    # THEN
    assert output == expected_output


@pytest.mark.parametrize("pydantic_mode", [1, _PYDANTIC_VERSION])
@pytest.mark.parametrize(
    "entrypoint,kwargs_list,expected_files",
    (
        pytest.param(
            "tests.script_runner.artifact_serialisers_vX:base_model_auto_save",
            [
                {"name": "a", "value": "hello "},
                {"name": "b", "value": "world"},
            ],
            [
                {
                    "subpath": "tmp/hera-outputs/artifacts/my-output-artifact",
                    "value": json.dumps({"a": "hello ", "b": "world"}),
                }
            ],
            id="save-base-models-automatically",
        ),
        pytest.param(
            "tests.script_runner.artifact_serialisers_vX:non_base_model_with_class_serialiser",
            [
                {"name": "a", "value": "hello "},
                {"name": "b", "value": "world"},
            ],
            [
                {
                    "subpath": "tmp/hera-outputs/artifacts/my-output-artifact",
                    "value": json.dumps({"a": "hello ", "b": "world"}),
                }
            ],
            id="save-non-base-model-with-class-loader",
        ),
        pytest.param(
            "tests.script_runner.artifact_serialisers_vX:pydantic_output_with_dumper_on_attribute",
            [
                {"name": "a", "value": "hello "},
                {"name": "b", "value": "world"},
            ],
            [
                {
                    "subpath": "tmp/hera-outputs/artifacts/my-output-artifact",
                    "value": json.dumps({"a": "hello ", "b": "world"}),
                }
            ],
            id="save-pydantic-output-with-custom-field-serialiser",
        ),
    ),
)
def test_artifact_dumping(
    entrypoint: str,
    kwargs_list: List[Dict[str, str]],
    expected_files: List[Dict[str, str]],
    pydantic_mode: int,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    # GIVEN
    outputs_directory = str(tmp_path / "tmp/hera-outputs")
    monkeypatch.setenv("hera__outputs_directory", outputs_directory)
    monkeypatch.setenv("hera__pydantic_mode", str(pydantic_mode))
    monkeypatch.setenv("hera__script_pydantic_io", "")
    entrypoint = entrypoint.replace("artifact_serialisers_vX", f"artifact_serialisers_v{pydantic_mode}")

    # WHEN
    output = _runner(entrypoint, kwargs_list)

    # THEN
    assert output is None or isinstance(output, (OutputV1, OutputV2)), (
        "Runner should not return values directly when using return Annotations"
    )  # (not for Output objects)
    for file in expected_files:
        assert Path(tmp_path / file["subpath"]).is_file()
        assert Path(tmp_path / file["subpath"]).read_text() == file["value"]


@pytest.mark.parametrize("pydantic_mode", [1, _PYDANTIC_VERSION])
@pytest.mark.parametrize(
    "entrypoint,kwargs_list,expected_files",
    (
        pytest.param(
            "tests.script_runner.artifact_serialisers_vX:bytes_dumper",
            [
                {"name": "a", "value": "hello "},
                {"name": "b", "value": "world"},
            ],
            [
                {
                    "subpath": "tmp/hera-outputs/artifacts/my-output-artifact",
                    "value": pickle.dumps("hello world".encode("utf-8")),
                }
            ],
            id="save-bytes",
        ),
    ),
)
def test_artifact_byte_dumping(
    entrypoint: str,
    kwargs_list: List[Dict[str, str]],
    expected_files: List[Dict[str, str]],
    pydantic_mode: int,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    # GIVEN
    outputs_directory = str(tmp_path / "tmp/hera-outputs")
    monkeypatch.setenv("hera__outputs_directory", outputs_directory)
    monkeypatch.setenv("hera__pydantic_mode", str(pydantic_mode))
    monkeypatch.setenv("hera__script_pydantic_io", "")
    entrypoint = entrypoint.replace("artifact_serialisers_vX", f"artifact_serialisers_v{pydantic_mode}")

    # WHEN
    output = _runner(entrypoint, kwargs_list)

    # THEN
    assert output is None
    for file in expected_files:
        assert Path(tmp_path / file["subpath"]).is_file()
        assert Path(tmp_path / file["subpath"]).read_bytes() == file["value"]
