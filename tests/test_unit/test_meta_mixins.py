from pathlib import Path
from typing import Annotated

from hera.workflows import Artifact, Parameter
from hera.workflows._meta_mixins import _get_param_items_from_source


def test_get_param_items_from_source_simple_function_one_param():
    def function(some_param: str) -> None: ...

    parameters = _get_param_items_from_source(function)

    assert parameters == [Parameter(name="some_param", value="{{item}}")]


def test_get_param_items_from_source_simple_function_multiple_params():
    def function(foo: str, bar: int, baz: str) -> None: ...

    parameters = _get_param_items_from_source(function)

    assert parameters == [
        Parameter(name="foo", value="{{item.foo}}"),
        Parameter(name="bar", value="{{item.bar}}"),
        Parameter(name="baz", value="{{item.baz}}"),
    ]


def test_get_param_items_from_source_simple_function_defaulted_params_skipped():
    def function(some_param: str, defaulted_param: str = "some value") -> None: ...

    parameters = _get_param_items_from_source(function)

    assert parameters == [Parameter(name="some_param", value="{{item}}")]


def test_get_param_items_from_source_annotated_function_one_param():
    def function(some_param: Annotated[str, Parameter(name="foobar")]) -> None: ...

    parameters = _get_param_items_from_source(function)

    assert parameters == [Parameter(name="foobar", value="{{item}}")]


def test_get_param_items_from_source_annotated_function_multiple_params():
    def function(
        foo: Annotated[str, Parameter(name="foobar")],
        bar: int,
        baz: Annotated[str, Parameter(description="some description")],
    ) -> None: ...

    parameters = _get_param_items_from_source(function)

    assert parameters == [
        Parameter(name="foobar", value="{{item.foobar}}"),
        Parameter(name="bar", value="{{item.bar}}"),
        Parameter(name="baz", value="{{item.baz}}", description="some description"),
    ]


def test_get_param_items_from_source_annotated_function_defaulted_params_skipped():
    def function(
        some_param: Annotated[str, Parameter(name="some-param")],
        defaulted_param: Annotated[str, Parameter(name="bazbam")] = "some value",
    ) -> None: ...

    parameters = _get_param_items_from_source(function)

    assert parameters == [Parameter(name="some-param", value="{{item}}")]


def test_get_param_items_from_source_annotated_function_outputs_skipped():
    def function(
        some_param: Annotated[str, Parameter(name="some-param")], output_param: Annotated[Path, Parameter(output=True)]
    ) -> None: ...

    parameters = _get_param_items_from_source(function)

    assert parameters == [Parameter(name="some-param", value="{{item}}")]


def test_get_param_items_from_source_annotated_function_artifacts_skipped():
    def function(
        some_param: Annotated[str, Parameter(name="some-param")], some_resource: Annotated[str, Artifact()]
    ) -> None: ...

    parameters = _get_param_items_from_source(function)

    assert parameters == [Parameter(name="some-param", value="{{item}}")]
