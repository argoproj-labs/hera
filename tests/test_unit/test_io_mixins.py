from hera.workflows.io import Input
from hera.workflows.parameter import Parameter

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated


def test_input_mixin_get_parameters():
    class Foo(Input):
        foo: Annotated[int, Parameter(name="foo")]

    assert Foo._get_parameters() == [Parameter(name="foo")]


def test_input_mixin_get_parameters_default_name():
    class Foo(Input):
        foo: Annotated[int, Parameter(description="a foo")]

    assert Foo._get_parameters() == [Parameter(name="foo", description="a foo")]
