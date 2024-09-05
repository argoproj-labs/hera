import sys

if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated

from pydantic import Field

from hera.workflows import Artifact, Input, Parameter
from hera.workflows.models import (
    Arguments as ModelArguments,
    Artifact as ModelArtifact,
    Parameter as ModelParameter,
)


def test_input_mixin_get_parameters():
    class Foo(Input):
        foo: Annotated[int, Parameter(name="foo")]

    assert Foo._get_parameters() == [Parameter(name="foo")]


def test_input_mixin_get_parameters_default_name():
    class Foo(Input):
        foo: Annotated[int, Parameter(description="a foo")]

    assert Foo._get_parameters() == [Parameter(name="foo", description="a foo")]


def test_get_as_arguments_unannotated():
    class Foo(Input):
        foo: int
        bar: str = "a default"

    foo = Foo(foo=1)
    parameters = foo._get_as_arguments()

    assert parameters == ModelArguments(
        parameters=[
            ModelParameter(name="foo", value=1),
            ModelParameter(name="bar", value="a default"),
        ],
    )


def test_get_as_arguments_with_pydantic_annotations():
    class Foo(Input):
        foo: Annotated[int, Field(gt=0)]
        bar: Annotated[str, Field(max_length=10)] = "a default"

    foo = Foo(foo=1)
    parameters = foo._get_as_arguments()

    assert parameters == ModelArguments(
        parameters=[
            ModelParameter(name="foo", value=1),
            ModelParameter(name="bar", value="a default"),
        ]
    )


def test_get_as_arguments_annotated_with_name():
    class Foo(Input):
        foo: Annotated[int, Parameter(name="f_oo")]
        bar: Annotated[str, Parameter(name="b_ar")] = "a default"
        baz: Annotated[str, Artifact(name="b_az")]

    foo = Foo(foo=1, baz="previous step")
    parameters = foo._get_as_arguments()

    assert parameters == ModelArguments(
        artifacts=[
            ModelArtifact(name="b_az", from_="previous step"),
        ],
        parameters=[
            ModelParameter(name="f_oo", value=1),
            ModelParameter(name="b_ar", value="a default"),
        ],
    )


def test_get_as_arguments_annotated_with_description():
    class Foo(Input):
        foo: Annotated[int, Parameter(description="param foo")]
        bar: Annotated[str, Parameter(description="param bar")] = "a default"
        baz: Annotated[str, Artifact(description="artifact baz")]

    foo = Foo(foo=1, baz="previous step")
    parameters = foo._get_as_arguments()

    assert parameters == ModelArguments(
        artifacts=[
            ModelArtifact(name="baz", from_="previous step"),
        ],
        parameters=[
            ModelParameter(name="foo", value=1),
            ModelParameter(name="bar", value="a default"),
        ],
    )


def test_get_as_arguments_with_multiple_annotations():
    class Foo(Input):
        foo: Annotated[int, Parameter(name="f_oo"), Field(gt=0)]
        bar: Annotated[str, Field(max_length=10), Parameter(description="param bar")] = "a default"
        baz: Annotated[str, Field(max_length=15), Artifact()]

    foo = Foo(foo=1, baz="previous step")
    parameters = foo._get_as_arguments()

    assert parameters == ModelArguments(
        artifacts=[
            ModelArtifact(name="baz", from_="previous step"),
        ],
        parameters=[
            ModelParameter(name="f_oo", value=1),
            ModelParameter(name="bar", value="a default"),
        ],
    )
