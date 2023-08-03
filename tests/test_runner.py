import os

import pytest

from hera.shared.serialization import serialize
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
def test(entrypoint, kwargs_list, expected_output):
    # WHEN
    output = _runner(entrypoint, kwargs_list)

    # THEN
    assert serialize(output) == expected_output


@pytest.mark.parametrize(
    "entrypoint,file_contents,expected_output",
    [
        (
            "tests.artifact_annotations.script_annotations_artifact_path:read_artifact",
            "Hello there!",
            "Hello there!",
        ),
        (
            "tests.artifact_annotations.script_annotations_artifact_object:read_artifact",
            """{"a": "Hello ", "b": "there!"}""",
            "Hello there!",
        ),
        (
            "tests.artifact_annotations.script_annotations_artifact_file:read_artifact",
            "Hello there!",
            "Hello there!",
        ),
        (
            "tests.artifact_annotations.script_annotations_artifact_file_with_path:read_artifact",
            "/this/is/a/path",
            "/this/is/a/path",
        ),
    ],
)
def test_artifact(entrypoint, file_contents, expected_output, tmp_path, monkeypatch, global_config_fixture):
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
    ["tests.artifact_annotations.script_annotations_artifact_wrong_loader:read_artifact"],
)
def test_artifact_wrong_loader(entrypoint, global_config_fixture):
    # GIVEN
    kwargs_list = []
    global_config_fixture.experimental_features["script_annotations"] = True
    os.environ["hera__script_annotations"] = ""

    # WHEN
    with pytest.raises(ValueError) as e:
        _runner(entrypoint, kwargs_list)

    # THEN
    assert "value is not a valid enumeration member" in str(e.value)
