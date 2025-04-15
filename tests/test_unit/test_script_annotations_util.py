import json
import os
from pathlib import Path
from typing import Any, Callable, Optional, Union

import pytest

from hera.workflows._runner.script_annotations_util import (
    _get_outputs_path,
    get_annotated_artifact_value,
    get_annotated_input_param,
    get_annotated_output_param,
    load_param_input,
    map_runner_input,
)
from hera.workflows.artifact import Artifact, ArtifactLoader
from hera.workflows.io import Input
from hera.workflows.models import ValueFrom
from hera.workflows.parameter import Parameter

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated


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
    ],
)
def test_get_annotated_input_param(
    func_param_name,
    param_annotation,
    kwargs,
    expected_value,
):
    assert get_annotated_input_param(func_param_name, param_annotation, kwargs) == expected_value


@pytest.mark.parametrize(
    "param_value,loader,expected_value",
    [
        pytest.param("hello", None, "hello", id="string-no-loader"),
        pytest.param("hello", lambda _: "other", "other", id="string-loader"),
    ],
)
def test_load_param_input(
    param_value: str,
    loader: Optional[Callable[[str], Any]],
    expected_value: str,
):
    assert (
        load_param_input(
            param_value,
            loader,
        )
        == expected_value
    )


@pytest.mark.parametrize(
    "param_annotation,expected_value",
    [
        pytest.param(
            Parameter(name="output-default-path-test", output=True),
            Path("/tmp/hera-outputs/parameters/output-default-path-test"),
            id="output-parameter-with-default",
        ),
        pytest.param(
            Parameter(name="output-path-test", value_from=ValueFrom(path="/tmp/test"), output=True),
            Path("/tmp/test"),
            id="output-parameter-with-custom-path",
        ),
    ],
)
def test_get_annotated_output_param(
    param_annotation,
    expected_value,
):
    assert get_annotated_output_param(param_annotation) == expected_value


def test_get_annotated_input_param_error():
    with pytest.raises(RuntimeError, match="my_func_param was not given a value"):
        get_annotated_input_param("my_func_param", Parameter(), {})


def test_get_annotated_input_param_error_param_name():
    with pytest.raises(RuntimeError, match="my-func-param was not given a value"):
        get_annotated_input_param("my_func_param", Parameter(name="my-func-param"), {})


@pytest.mark.parametrize(
    "file_contents,artifact,param_type,expected_return",
    [
        pytest.param(
            '{"json": "object"}', Artifact(loader=ArtifactLoader.json), dict, {"json": "object"}, id="json-load"
        ),
        pytest.param(
            '{"json": "object"}', Artifact(loader=ArtifactLoader.file), str, '{"json": "object"}', id="file-load"
        ),
    ],
)
def test_get_annotated_artifact_value_inputs_with_loaders(
    file_contents: str,
    artifact: Artifact,
    param_type: type,
    expected_return: Any,
    tmp_path: Path,
):
    file_path = tmp_path / "contents.txt"
    file_path.write_text(file_contents)
    artifact.path = file_path
    assert get_annotated_artifact_value(artifact, param_type) == expected_return


@pytest.mark.parametrize(
    "file_contents,artifact,param_type",
    [
        pytest.param('{"json": "object"}', Artifact(loader=None), Path, id="file-load"),
    ],
)
def test_get_annotated_artifact_value_path_inputs(
    file_contents: str,
    artifact: Artifact,
    param_type: type,
    tmp_path: Path,
):
    file_path = tmp_path / "contents.txt"
    file_path.write_text(file_contents)
    artifact.path = file_path
    assert get_annotated_artifact_value(artifact, param_type) == file_path


@pytest.mark.parametrize(
    "artifact,param_type,expected_path",
    [
        pytest.param(Artifact(path="/tmp/test.txt", output=True), Path, "/tmp/test.txt", id="given-path"),
        pytest.param(
            Artifact(name="artifact-name", output=True),
            Path,
            "/tmp/hera-outputs/artifacts/artifact-name",
            id="default-path",
        ),
    ],
)
def test_get_annotated_artifact_value_path_outputs(
    artifact: Artifact,
    param_type: type,
    expected_path: str,
):
    assert get_annotated_artifact_value(artifact, param_type) == Path(expected_path)


def test_map_runner_input():
    class MyInput(Input):
        a_str: str
        an_int: int
        a_dict: dict
        a_list: list

    kwargs = {
        "a_str": "hello",
        "an_int": "123",
        "a_dict": '{"a-key": "a-value"}',
        "a_list": json.dumps([1, 2, 3]),
    }
    assert map_runner_input(MyInput, kwargs) == MyInput(
        a_str="hello",
        an_int=123,
        a_dict={"a-key": "a-value"},
        a_list=[1, 2, 3],
    )


def test_map_runner_input_strings():
    """Test the parsing logic when str type fields are passed json-serialized strings."""

    class MyInput(Input):
        a_dict_str: str
        a_list_str: str

    kwargs = {"a_dict_str": json.dumps({"key": "value"}), "a_list_str": json.dumps([1, 2, 3])}
    assert map_runner_input(MyInput, kwargs) == MyInput(
        a_dict_str=json.dumps({"key": "value"}),
        a_list_str=json.dumps([1, 2, 3]),
    )


def test_map_runner_input_annotated_parameter():
    """Test annotated Parameter."""

    class Foo(Input):
        foo: Annotated[str, Parameter(name="bar")]

    kwargs = {"foo": "hello"}
    assert map_runner_input(Foo, kwargs) == Foo(foo="hello")
    kwargs = {"bar": "there"}
    assert map_runner_input(Foo, kwargs) == Foo(foo="there")


def test_map_runner_input_output_parameter_disallowed():
    """Test annotated output Parameter is not allowed."""

    class Foo(Input):
        foo: Annotated[str, Parameter(name="bar", output=True)]

    with pytest.raises(AssertionError):
        kwargs = {"foo": "hello"}
        map_runner_input(Foo, kwargs)


def test_map_runner_input_annotated_artifact(tmp_path):
    """Test annotated Artifact."""

    foo_path = tmp_path / "foo"
    foo_path.write_text("hello there")

    class Foo(Input):
        foo: Annotated[str, Artifact(name="bar", path=str(foo_path), loader=ArtifactLoader.file)]

    assert map_runner_input(Foo, {}) == Foo(foo="hello there")


def test_map_runner_input_annotated_inheritance():
    """Test model inheritance with Annotated fields."""

    class Foo(Input):
        foo: Annotated[str, Parameter(name="foo")]

    class FooBar(Foo):
        bar: Annotated[str, Parameter(name="bar")]

    kwargs = {"foo": "hello", "bar": "there"}
    assert map_runner_input(FooBar, kwargs) == FooBar(**kwargs)


def test_map_runner_input_annotated_inheritance_override():
    """Test model inheritance with Annotated fields."""

    class Foo(Input):
        foo: Annotated[str, Parameter(name="foo")]

    class FooBar(Foo):
        foo: Annotated[str, Parameter(name="bar")]

    kwargs = {"bar": "hello"}
    assert map_runner_input(FooBar, kwargs) == FooBar(foo="hello")


def test_map_runner_input_annotated_parameter_noname():
    """Test Annotated Parameter with no name."""

    class Foo(Input):
        foo: Annotated[str, Parameter(description="a parameter")]

    kwargs = {"foo": "hello"}
    assert map_runner_input(Foo, kwargs) == Foo(foo="hello")
