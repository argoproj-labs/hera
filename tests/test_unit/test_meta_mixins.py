from hera.workflows import Parameter
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
