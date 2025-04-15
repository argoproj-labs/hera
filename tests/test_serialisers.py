import json
from pathlib import Path
from typing import Any, Dict, List

import pytest

from hera.shared._pydantic import _PYDANTIC_VERSION
from hera.workflows._runner.util import _runner
from hera.workflows.io.v1 import Output as OutputV1

try:
    from hera.workflows.io.v2 import (  # type: ignore
        Output as OutputV2,
    )
except ImportError:
    from hera.workflows.io.v1 import (  # type: ignore
        Output as OutputV2,
    )


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
