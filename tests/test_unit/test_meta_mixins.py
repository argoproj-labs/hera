from pathlib import Path
from typing import Annotated

import pytest

from hera.shared.serialization import serialize
from hera.workflows import Artifact, Input, Parameter, Steps, Workflow, script
from hera.workflows._meta_mixins import _get_parameters_used_in_with_items, _get_unset_source_parameters_as_items


def test_get_param_items_from_source_simple_function_one_param():
    def function(some_param: str) -> None: ...

    parameters = _get_unset_source_parameters_as_items(function)

    assert parameters == [Parameter(name="some_param", value="{{item}}")]


def test_get_param_items_from_source_simple_function_multiple_params():
    def function(foo: str, bar: int, baz: str) -> None: ...

    parameters = _get_unset_source_parameters_as_items(function)

    assert parameters == [
        Parameter(name="foo", value="{{item.foo}}"),
        Parameter(name="bar", value="{{item.bar}}"),
        Parameter(name="baz", value="{{item.baz}}"),
    ]


def test_get_param_items_from_source_simple_function_defaulted_params_skipped():
    def function(some_param: str, defaulted_param: str = "some value") -> None: ...

    parameters = _get_unset_source_parameters_as_items(function)

    assert parameters == [Parameter(name="some_param", value="{{item}}")]


def test_get_param_items_from_source_annotated_function_one_param():
    def function(some_param: Annotated[str, Parameter(name="foobar")]) -> None: ...

    parameters = _get_unset_source_parameters_as_items(function)

    assert parameters == [Parameter(name="foobar", value="{{item}}")]


def test_get_param_items_from_source_annotated_function_multiple_params():
    def function(
        foo: Annotated[str, Parameter(name="foobar")],
        bar: int,
        baz: Annotated[str, Parameter(description="some description")],
    ) -> None: ...

    parameters = _get_unset_source_parameters_as_items(function)

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

    parameters = _get_unset_source_parameters_as_items(function)

    assert parameters == [Parameter(name="some-param", value="{{item}}")]


def test_get_param_items_from_source_annotated_function_outputs_skipped():
    def function(
        some_param: Annotated[str, Parameter(name="some-param")], output_param: Annotated[Path, Parameter(output=True)]
    ) -> None: ...

    parameters = _get_unset_source_parameters_as_items(function)

    assert parameters == [Parameter(name="some-param", value="{{item}}")]


def test_get_param_items_from_source_annotated_function_artifacts_skipped():
    def function(
        some_param: Annotated[str, Parameter(name="some-param")], some_resource: Annotated[str, Artifact()]
    ) -> None: ...

    parameters = _get_unset_source_parameters_as_items(function)

    assert parameters == [Parameter(name="some-param", value="{{item}}")]


def test_get_param_items_from_source_pydantic_input_one_param():
    class ExampleInput(Input):
        some_param: str

    def function(input: ExampleInput) -> None: ...

    parameters = _get_unset_source_parameters_as_items(function)

    assert parameters == [Parameter(name="some_param", value="{{item}}")]


def test_get_param_items_from_source_pydantic_input_multiple_params():
    class ExampleInput(Input):
        foo: Annotated[str, Parameter(name="foobar")]
        bar: int
        baz: Annotated[str, Parameter(description="some description")]

    def function(input: ExampleInput) -> None: ...

    parameters = _get_unset_source_parameters_as_items(function)

    assert parameters == [
        Parameter(name="foobar", value="{{item.foobar}}"),
        Parameter(name="bar", value="{{item.bar}}"),
        Parameter(name="baz", value="{{item.baz}}", description="some description"),
    ]


def test_get_param_items_from_source_pydantic_input_defaulted_params_skipped():
    class ExampleInput(Input):
        some_param: Annotated[str, Parameter(name="some-param")]
        defaulted_param: Annotated[str, Parameter(name="bazbam")] = "some value"

    def function(input: ExampleInput) -> None: ...

    parameters = _get_unset_source_parameters_as_items(function)

    assert parameters == [Parameter(name="some-param", value="{{item}}")]


def test_get_param_items_from_source_pydantic_input_artifacts_skipped():
    class ExampleInput(Input):
        some_param: Annotated[str, Parameter(name="some-param")]
        some_resource: Annotated[str, Artifact()]

    def function(input: ExampleInput) -> None: ...

    parameters = _get_unset_source_parameters_as_items(function)

    assert parameters == [Parameter(name="some-param", value="{{item}}")]


def test_get_parameters_used_in_with_items_empty():
    with_items_list = []

    parameters = _get_parameters_used_in_with_items(with_items_list)

    assert parameters is None


@pytest.mark.parametrize(
    "with_items_list",
    [
        ["a", "b", "c"],
        [1, 2, 3],
        [1.0, 2.0, 3.0],
        [True, False, True],
        [None, None, None],
        [serialize(item) for item in [{"a": "b"}, {"c": "d"}, {"e": "f"}]],
    ],
)
def test_get_parameters_used_in_with_items_list_of_non_dict(with_items_list):
    parameters = _get_parameters_used_in_with_items(with_items_list)

    assert parameters is None


def test_get_parameters_used_in_with_items_single_param():
    with_items_list = [{"some_param": "a value"}]

    parameters = _get_parameters_used_in_with_items(with_items_list)

    assert parameters == [Parameter(name="some_param", value="{{item}}")]


def test_get_parameters_used_in_with_items_multiple_params():
    with_items_list = [{"foo": "a value", "bar": "another value", "baz": "yet another value"}]

    parameters = _get_parameters_used_in_with_items(with_items_list)

    assert parameters == [
        Parameter(name="foo", value="{{item.foo}}"),
        Parameter(name="bar", value="{{item.bar}}"),
        Parameter(name="baz", value="{{item.baz}}"),
    ]


def test_callable_script_wrong_parameter_name_raises():
    @script()
    def print_message(message):
        print(message)

    with pytest.raises(ValueError, match="Parameter 'wrong-key' not found in source function 'print_message'"):
        with Workflow(generate_name="loops-", entrypoint="loop-bad-example"):
            with Steps(name="loop-bad-example"):
                print_message(
                    name="print-message-loop-with-items-dict",
                    with_items=[
                        {"wrong-key": "hello world"},
                        {"wrong-key": "goodbye world"},
                    ],
                )


def test_callable_script_non_matching_keys_raises():
    @script()
    def print_message(message):
        print(message)

    with pytest.raises(ValueError, match="All dictionaries in with_items must have the same keys"):
        with Workflow(generate_name="loops-", entrypoint="loop-bad-example"):
            with Steps(name="loop-bad-example"):
                print_message(
                    name="print-message-loop-with-items-dict",
                    with_items=[
                        {"wrong-key": "hello world"},
                        {"message": "goodbye world"},
                    ],
                )


@pytest.mark.parametrize(
    "with_items_list",
    [
        [{"message": "hello world"}, "goodbye world"],
        ["hello world", {"message": "goodbye world"}],
    ],
)
def test_callable_script_mixed_types_raises(with_items_list):
    @script()
    def print_message(message):
        print(message)

    with pytest.raises(ValueError, match="List must contain all dictionaries or no dictionaries"):
        with Workflow(generate_name="loops-", entrypoint="loop-bad-example"):
            with Steps(name="loop-bad-example"):
                print_message(
                    name="print-message-loop-with-items-dict",
                    with_items=with_items_list,
                )
