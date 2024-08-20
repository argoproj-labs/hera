from typing import Optional, Union

import pytest

try:
    from typing import Annotated  # type: ignore
except ImportError:
    from typing_extensions import Annotated  # type: ignore

from pathlib import Path

from hera.workflows import Workflow, script
from hera.workflows.artifact import Artifact
from hera.workflows.script import _get_inputs_from_callable


def test_get_inputs_from_callable_simple_params():
    # GIVEN
    def my_function(a: int, b: str):
        return a + b

    # WHEN
    params, artifacts = _get_inputs_from_callable(my_function)

    # THEN
    assert params is not None
    assert artifacts == []

    assert isinstance(params, list)
    assert len(params) == 2
    a = params[0]
    b = params[1]

    assert a.name == "a"
    assert b.name == "b"


def test_get_inputs_from_callable_no_params():
    # GIVEN
    def no_param_function():
        return "Hello there!"

    # WHEN
    params, artifacts = _get_inputs_from_callable(no_param_function)

    # THEN
    assert params == []
    assert artifacts == []


def test_get_artifact_input():
    # GIVEN
    def input_artifact_function(an_artifact: Annotated[Path, Artifact(name="my-artifact", path="my-file.txt")]) -> str:
        return an_artifact.read_text()

    # WHEN
    params, artifacts = _get_inputs_from_callable(input_artifact_function)

    # THEN
    assert params == []
    assert isinstance(artifacts, list)
    assert len(artifacts) == 1
    an_artifact = artifacts[0]

    assert an_artifact.name == "my-artifact"
    assert an_artifact.path == "my-file.txt"


def test_script_name_kwarg_in_decorator():
    # GIVEN
    @script(name="my-alt-name")
    def my_func():
        print("Hello world!")

    # WHEN
    with Workflow(name="test-script") as w:
        my_func()

    # THEN
    assert w.templates[0].name == "my-alt-name"


def test_script_parses_static_method():
    class Test:
        @script()
        @staticmethod
        def my_func():
            print(42)

        @script(name="test")
        @staticmethod
        def my_func2():
            print(42)

    # GIVEN my_func above
    # WHEN
    with Workflow(name="test-script") as w:
        Test.my_func()
        Test.my_func2()

    # THEN
    assert len(w.templates) == 2
    assert w.templates[0].name == "my-func"
    assert w.templates[1].name == "test"


def test_script_ignores_unknown_annotations():
    # GIVEN
    @script()
    def unknown_annotations_ignored(my_string: Annotated[str, "some metadata"]) -> str:
        return my_string

    # WHEN
    params, artifacts = _get_inputs_from_callable(unknown_annotations_ignored)

    # THEN
    assert artifacts == []
    assert isinstance(params, list)
    assert len(params) == 1
    parameter = params[0]

    assert parameter.name == "my_string"
    assert parameter.default is None


def test_script_optional_parameter():
    # GIVEN
    @script()
    def unknown_annotations_ignored(my_optional_string: Optional[str] = None) -> str:
        return "Got: {}".format(my_optional_string)

    # WHEN
    params, artifacts = _get_inputs_from_callable(unknown_annotations_ignored)

    # THEN
    assert artifacts == []
    assert isinstance(params, list)
    assert len(params) == 1
    parameter = params[0]

    assert parameter.name == "my_optional_string"
    assert parameter.default == "null"


def test_invalid_script_when_optional_parameter_does_not_have_default_value():
    @script()
    def unknown_annotations_ignored(my_optional_string: Optional[str]) -> str:
        return "Got: {}".format(my_optional_string)

    with pytest.raises(ValueError, match="Optional parameter 'my_optional_string' doesn't have default value."):
        _get_inputs_from_callable(unknown_annotations_ignored)


def test_invalid_script_when_optional_parameter_does_not_have_default_value_2():
    @script()
    def unknown_annotations_ignored(my_optional_string: Annotated[Optional[str], "123"]) -> str:
        return "Got: {}".format(my_optional_string)

    with pytest.raises(ValueError, match="Optional parameter 'my_optional_string' doesn't have default value."):
        _get_inputs_from_callable(unknown_annotations_ignored)


def test_invalid_script_when_optional_parameter_does_not_have_default_value_3():
    @script()
    def unknown_annotations_ignored(my_optional_string: Union[str, None]) -> str:
        return "Got: {}".format(my_optional_string)

    with pytest.raises(ValueError, match="Optional parameter 'my_optional_string' doesn't have default value."):
        _get_inputs_from_callable(unknown_annotations_ignored)


def test_invalid_script_when_optional_parameter_does_not_have_default_value_4():
    @script()
    def unknown_annotations_ignored(my_optional_string: Union[None, str]) -> str:
        return "Got: {}".format(my_optional_string)

    with pytest.raises(ValueError, match="Optional parameter 'my_optional_string' doesn't have default value."):
        _get_inputs_from_callable(unknown_annotations_ignored)
