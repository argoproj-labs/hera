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


def test_get_parameters_unannotated():
    class Foo(Input):
        foo: int
        bar: str = "a default"

    assert Foo._get_parameters() == [
        Parameter(name="foo"),
        Parameter(name="bar", default="a default"),
    ]


def test_get_parameters_with_pydantic_annotations():
    class Foo(Input):
        foo: Annotated[int, Field(gt=0)]
        bar: Annotated[str, Field(max_length=10)] = "a default"

    assert Foo._get_parameters() == [
        Parameter(name="foo"),
        Parameter(name="bar", default="a default"),
    ]


def test_get_parameters_annotated_with_name():
    class Foo(Input):
        foo: Annotated[int, Parameter(name="f_oo")]
        bar: Annotated[str, Parameter(name="b_ar")] = "a default"
        baz: Annotated[str, Artifact(name="b_az")]

    assert Foo._get_parameters() == [
        Parameter(name="f_oo"),
        Parameter(name="b_ar", default="a default"),
    ]


def test_get_parameters_annotated_with_description():
    class Foo(Input):
        foo: Annotated[int, Parameter(description="param foo")]
        bar: Annotated[str, Parameter(description="param bar")] = "a default"
        baz: Annotated[str, Artifact(description="artifact baz")]

    assert Foo._get_parameters() == [
        Parameter(name="foo", description="param foo"),
        Parameter(name="bar", default="a default", description="param bar"),
    ]


def test_get_parameters_with_multiple_annotations():
    class Foo(Input):
        foo: Annotated[int, Parameter(name="f_oo"), Field(gt=0)]
        bar: Annotated[str, Field(max_length=10), Parameter(description="param bar")] = "a default"
        baz: Annotated[str, Field(max_length=15), Artifact()]

    assert Foo._get_parameters() == [
        Parameter(name="f_oo"),
        Parameter(name="bar", default="a default", description="param bar"),
    ]


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


def test_get_as_templated_arguments_unannotated():
    class Foo(Input):
        foo: int
        bar: str = "a default"

    templated_arguments = Foo._get_as_templated_arguments()

    assert templated_arguments == Foo.construct(
        foo="{{inputs.parameters.foo}}",
        bar="{{inputs.parameters.bar}}",
    )


def test_get_as_templated_arguments_with_pydantic_annotations():
    class Foo(Input):
        foo: Annotated[int, Field(gt=0)]
        bar: Annotated[str, Field(max_length=10)] = "a default"

    templated_arguments = Foo._get_as_templated_arguments()

    assert templated_arguments == Foo.construct(
        foo="{{inputs.parameters.foo}}",
        bar="{{inputs.parameters.bar}}",
    )


def test_get_as_templated_arguments_annotated_with_name():
    class Foo(Input):
        foo: Annotated[int, Parameter(name="f_oo")]
        bar: Annotated[str, Parameter(name="b_ar")] = "a default"
        baz: Annotated[str, Artifact(name="b_az")]

    templated_arguments = Foo._get_as_templated_arguments()

    assert templated_arguments == Foo.construct(
        foo="{{inputs.parameters.f_oo}}",
        bar="{{inputs.parameters.b_ar}}",
        baz="{{inputs.artifacts.b_az}}",
    )


def test_get_as_templated_arguments_annotated_with_description():
    class Foo(Input):
        foo: Annotated[int, Parameter(description="param foo")]
        bar: Annotated[str, Parameter(description="param bar")] = "a default"
        baz: Annotated[str, Artifact(description="artifact baz")]

    templated_arguments = Foo._get_as_templated_arguments()

    assert templated_arguments == Foo.construct(
        foo="{{inputs.parameters.foo}}",
        bar="{{inputs.parameters.bar}}",
        baz="{{inputs.artifacts.baz}}",
    )


def test_get_as_templated_arguments_with_multiple_annotations():
    class Foo(Input):
        foo: Annotated[int, Parameter(name="f_oo"), Field(gt=0)]
        bar: Annotated[str, Field(max_length=10), Parameter(description="param bar")] = "a default"
        baz: Annotated[str, Field(max_length=15), Artifact()]

    templated_arguments = Foo._get_as_templated_arguments()

    assert templated_arguments == Foo.construct(
        foo="{{inputs.parameters.f_oo}}",
        bar="{{inputs.parameters.bar}}",
        baz="{{inputs.artifacts.baz}}",
    )
