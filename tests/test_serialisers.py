import json
from typing import Any, Dict, List

import pytest

from hera.shared.serialization import serialize
from hera.workflows._runner.util import _runner


@pytest.mark.parametrize(
    "entrypoint,kwargs_list,expected_output",
    (
        pytest.param(
            "tests.script_runner.serialisers_v1:base_model_auto_load",
            [{"name": "my-parameter", "value": json.dumps({"a": "hello ", "b": "world"})}],
            "hello world",
            id="load-base-models-automatically",
        ),
        pytest.param(
            "tests.script_runner.serialisers_v1:non_base_model_with_class_loader",
            [{"name": "my-parameter", "value": json.dumps({"a": "hello ", "b": "world"})}],
            "hello world",
            id="load-non-base-model-with-class-loader",
        ),
        pytest.param(
            "tests.script_runner.serialisers_v1:non_base_model_with_lambda_function_loader",
            [{"name": "my-parameter", "value": json.dumps({"a": "hello ", "b": "world"})}],
            "hello world",
            id="load-non-base-model-with-lambda-function-loader",
        ),
    ),
)
def test_parameter_loading(
    entrypoint: str,
    kwargs_list: List[Dict[str, str]],
    expected_output: Any,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv("hera__pydantic_mode", str(1))
    # WHEN
    output = _runner(entrypoint, kwargs_list)

    # THEN
    assert output == expected_output


@pytest.mark.parametrize("pydantic_mode", [1])  # , _PYDANTIC_VERSION])
@pytest.mark.parametrize(
    "entrypoint,kwargs_list,expected_output",
    [
        pytest.param(
            "tests.script_runner.serialisers_vX:pydantic_input_with_loader_on_attribute",
            [{"name": "my-parameter", "value": json.dumps({"a": "hello ", "b": "world"})}],
            "hello world",
            id="pydantic-input-with-loader-on-attribute",
        ),
    ],
)
def test_runner_pydantic_inputs_params(
    entrypoint,
    kwargs_list: List[Dict[str, str]],
    expected_output,
    pydantic_mode,
    monkeypatch: pytest.MonkeyPatch,
):
    # GIVEN
    entrypoint = entrypoint.replace("serialisers_vX", f"serialisers_v{pydantic_mode}")
    monkeypatch.setenv("hera__pydantic_mode", str(pydantic_mode))
    monkeypatch.setenv("hera__script_pydantic_io", "")

    # WHEN
    output = _runner(entrypoint, kwargs_list)

    # THEN
    assert serialize(output) == expected_output
