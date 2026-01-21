from typing import Annotated

from pydantic import Field

from hera.workflows import Artifact, Input, Output, Parameter
from hera.workflows.models import (
    Arguments as ModelArguments,
    Artifact as ModelArtifact,
    Parameter as ModelParameter,
    ValueFrom,
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
        baz: Annotated[str, Artifact()]

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


def test_get_artifacts_unannotated():
    class Foo(Input):
        foo: int
        bar: str = "a default"

    assert Foo._get_artifacts(add_missing_path=True) == []


def test_get_artifacts_with_pydantic_annotations():
    class Foo(Input):
        foo: Annotated[int, Field(gt=0)]
        bar: Annotated[str, Field(max_length=10)] = "a default"

    assert Foo._get_artifacts(add_missing_path=True) == []


def test_get_artifacts_annotated_with_name():
    class Foo(Input):
        foo: Annotated[int, Parameter(name="f_oo")]
        bar: Annotated[str, Parameter(name="b_ar")] = "a default"
        baz: Annotated[str, Artifact(name="b_az")]

    assert Foo._get_artifacts(add_missing_path=True) == [Artifact(name="b_az", path="/tmp/hera-inputs/artifacts/b_az")]


def test_get_artifacts_annotated_with_description():
    class Foo(Input):
        foo: Annotated[int, Parameter(description="param foo")]
        bar: Annotated[str, Parameter(description="param bar")] = "a default"
        baz: Annotated[str, Artifact()]

    assert Foo._get_artifacts(add_missing_path=True) == [
        Artifact(
            name="baz",
            path="/tmp/hera-inputs/artifacts/baz",
        )
    ]


def test_get_artifacts_annotated_with_path():
    class Foo(Input):
        baz: Annotated[str, Artifact(path="/tmp/hera-inputs/artifacts/bishbosh")]

    assert Foo._get_artifacts(add_missing_path=True) == [
        Artifact(name="baz", path="/tmp/hera-inputs/artifacts/bishbosh")
    ]


def test_get_artifacts_annotated_do_not_add_path():
    class Foo(Input):
        baz: Annotated[str, Artifact()]

    assert Foo._get_artifacts(add_missing_path=False) == [Artifact(name="baz")]


def test_get_artifacts_with_multiple_annotations():
    class Foo(Input):
        foo: Annotated[int, Parameter(name="f_oo"), Field(gt=0)]
        bar: Annotated[str, Field(max_length=10), Parameter(description="param bar")] = "a default"
        baz: Annotated[str, Field(max_length=15), Artifact()]

    assert Foo._get_artifacts(add_missing_path=True) == [Artifact(name="baz", path="/tmp/hera-inputs/artifacts/baz")]


def test_get_as_arguments_unannotated():
    class Foo(Input):
        foo: int
        bar: str = "a default"

    foo = Foo(foo=1)
    parameters = foo._get_as_arguments()

    assert parameters == ModelArguments(
        parameters=[
            ModelParameter(name="foo", value="1"),
            ModelParameter(name="bar", value="a default"),
        ],
    )


def test_get_as_arguments_unannotated_v1():
    from hera.workflows.io.v1 import Input as InputV1

    class Foo(InputV1):
        foo: int
        bar: str = "a default"

    foo = Foo(foo=1)
    parameters = foo._get_as_arguments()

    assert parameters == ModelArguments(
        parameters=[
            ModelParameter(name="foo", value="1"),
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
            ModelParameter(name="foo", value="1"),
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
            ModelParameter(name="f_oo", value="1"),
            ModelParameter(name="b_ar", value="a default"),
        ],
    )


def test_get_as_arguments_annotated_with_description():
    class Foo(Input):
        foo: Annotated[int, Parameter(description="param foo")]
        bar: Annotated[str, Parameter(description="param bar")] = "a default"
        baz: Annotated[str, Artifact()]

    foo = Foo(foo=1, baz="previous step")
    parameters = foo._get_as_arguments()

    assert parameters == ModelArguments(
        artifacts=[
            ModelArtifact(name="baz", from_="previous step"),
        ],
        parameters=[
            ModelParameter(name="foo", value="1"),
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
            ModelParameter(name="f_oo", value="1"),
            ModelParameter(name="bar", value="a default"),
        ],
    )


def test_get_as_templated_arguments_unannotated():
    class Foo(Input):
        foo: int
        bar: str = "a default"

    templated_arguments = Foo._get_as_templated_arguments()

    assert templated_arguments == Foo.model_construct(
        foo="{{inputs.parameters.foo}}",
        bar="{{inputs.parameters.bar}}",
    )


def test_get_as_templated_arguments_with_pydantic_annotations():
    class Foo(Input):
        foo: Annotated[int, Field(gt=0)]
        bar: Annotated[str, Field(max_length=10)] = "a default"

    templated_arguments = Foo._get_as_templated_arguments()

    assert templated_arguments == Foo.model_construct(
        foo="{{inputs.parameters.foo}}",
        bar="{{inputs.parameters.bar}}",
    )


def test_get_as_templated_arguments_annotated_with_name():
    class Foo(Input):
        foo: Annotated[int, Parameter(name="f_oo")]
        bar: Annotated[str, Parameter(name="b_ar")] = "a default"
        baz: Annotated[str, Artifact(name="b_az")]

    templated_arguments = Foo._get_as_templated_arguments()

    assert templated_arguments == Foo.model_construct(
        foo="{{inputs.parameters.f_oo}}",
        bar="{{inputs.parameters.b_ar}}",
        baz="{{inputs.artifacts.b_az}}",
    )


def test_get_as_templated_arguments_annotated_with_description():
    class Foo(Input):
        foo: Annotated[int, Parameter(description="param foo")]
        bar: Annotated[str, Parameter(description="param bar")] = "a default"
        baz: Annotated[str, Artifact()]

    templated_arguments = Foo._get_as_templated_arguments()

    assert templated_arguments == Foo.model_construct(
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

    assert templated_arguments == Foo.model_construct(
        foo="{{inputs.parameters.f_oo}}",
        bar="{{inputs.parameters.bar}}",
        baz="{{inputs.artifacts.baz}}",
    )


def test_get_outputs_no_path_unannotated():
    class Foo(Output):
        foo: int
        fum: int = 5
        bar: str = "a default"

    parameters = Foo._get_outputs()

    assert parameters == [
        Parameter(name="foo"),
        Parameter(name="fum", default=5),
        Parameter(name="bar", default="a default"),
    ]


def test_get_outputs_no_path_with_pydantic_annotations():
    class Foo(Output):
        foo: Annotated[int, Field(gt=0)]
        fum: Annotated[int, Field(lt=1000)] = 5
        bar: Annotated[str, Field(max_length=10)] = "a default"

    parameters = Foo._get_outputs()

    assert parameters == [
        Parameter(name="foo"),
        Parameter(name="fum", default=5),
        Parameter(name="bar", default="a default"),
    ]


def test_get_outputs_no_path_annotated_with_name():
    class Foo(Output):
        foo: Annotated[int, Parameter(name="f_oo")]
        fum: Annotated[int, Parameter(name="f_um")] = 5
        bar: Annotated[str, Parameter(name="b_ar")] = "a default"
        baz: Annotated[str, Artifact(name="b_az")]

    parameters = Foo._get_outputs()

    assert parameters == [
        Parameter(name="f_oo"),
        Parameter(name="f_um", default=5),
        Parameter(name="b_ar", default="a default"),
        Artifact(name="b_az"),
    ]


def test_get_outputs_no_path_annotated_with_path():
    class Foo(Output):
        foo: Annotated[int, Parameter(value_from=ValueFrom(path="/tmp/one"))]
        fum: Annotated[int, Parameter(value_from=ValueFrom(path="/tmp/two"))] = 5
        bar: Annotated[str, Parameter(value_from=ValueFrom(path="/tmp/three"))] = "a default"
        baz: Annotated[str, Artifact(path="/tmp/four")]

    parameters = Foo._get_outputs()

    assert parameters == [
        Parameter(name="foo", value_from=ValueFrom(path="/tmp/one")),
        Parameter(name="fum", default=5, value_from=ValueFrom(path="/tmp/two")),
        Parameter(name="bar", default="a default", value_from=ValueFrom(path="/tmp/three")),
        Artifact(name="baz", path="/tmp/four"),
    ]


def test_get_outputs_no_path_annotated_with_description():
    class Foo(Output):
        foo: Annotated[int, Parameter(description="param foo")]
        fum: Annotated[int, Parameter(description="param fum")] = 5
        bar: Annotated[str, Parameter(description="param bar")] = "a default"
        baz: Annotated[str, Artifact()]

    parameters = Foo._get_outputs()

    assert parameters == [
        Parameter(name="foo", description="param foo"),
        Parameter(name="fum", description="param fum", default=5),
        Parameter(name="bar", default="a default", description="param bar"),
        Artifact(name="baz"),
    ]


def test_get_outputs_no_path_with_multiple_annotations():
    class Foo(Output):
        foo: Annotated[int, Parameter(name="f_oo"), Field(gt=0)]
        fum: Annotated[int, Field(lt=10000), Parameter(name="f_um")] = 5
        bar: Annotated[str, Field(max_length=10), Parameter(description="param bar")] = "a default"
        baz: Annotated[str, Field(max_length=15), Artifact()]

    parameters = Foo._get_outputs()

    assert parameters == [
        Parameter(name="f_oo"),
        Parameter(name="f_um", default=5),
        Parameter(name="bar", default="a default", description="param bar"),
        Artifact(name="baz"),
    ]


def test_get_outputs_add_path_unannotated():
    class Foo(Output):
        foo: int
        fum: int = 5
        bar: str = "a default"

    parameters = Foo._get_outputs(add_missing_path=True)

    assert parameters == [
        Parameter(name="foo", value_from=ValueFrom(path="/tmp/hera-outputs/parameters/foo")),
        Parameter(name="fum", default=5, value_from=ValueFrom(path="/tmp/hera-outputs/parameters/fum")),
        Parameter(name="bar", default="a default", value_from=ValueFrom(path="/tmp/hera-outputs/parameters/bar")),
    ]


def test_get_outputs_add_path_with_pydantic_annotations():
    class Foo(Output):
        foo: Annotated[int, Field(gt=0)]
        fum: Annotated[int, Field(lt=1000)] = 5
        bar: Annotated[str, Field(max_length=10)] = "a default"

    parameters = Foo._get_outputs(add_missing_path=True)

    assert parameters == [
        Parameter(name="foo", value_from=ValueFrom(path="/tmp/hera-outputs/parameters/foo")),
        Parameter(name="fum", default=5, value_from=ValueFrom(path="/tmp/hera-outputs/parameters/fum")),
        Parameter(name="bar", default="a default", value_from=ValueFrom(path="/tmp/hera-outputs/parameters/bar")),
    ]


def test_get_outputs_add_path_annotated_with_name():
    class Foo(Output):
        foo: Annotated[int, Parameter(name="f_oo")]
        fum: Annotated[int, Parameter(name="f_um")] = 5
        bar: Annotated[str, Parameter(name="b_ar")] = "a default"
        baz: Annotated[str, Artifact(name="b_az")]

    parameters = Foo._get_outputs(add_missing_path=True)

    assert parameters == [
        Parameter(name="f_oo", value_from=ValueFrom(path="/tmp/hera-outputs/parameters/f_oo")),
        Parameter(name="f_um", default=5, value_from=ValueFrom(path="/tmp/hera-outputs/parameters/f_um")),
        Parameter(name="b_ar", default="a default", value_from=ValueFrom(path="/tmp/hera-outputs/parameters/b_ar")),
        Artifact(name="b_az", path="/tmp/hera-outputs/artifacts/b_az"),
    ]


def test_get_outputs_add_path_annotated_with_path():
    class Foo(Output):
        foo: Annotated[int, Parameter(value_from=ValueFrom(path="/tmp/one"))]
        fum: Annotated[int, Parameter(value_from=ValueFrom(path="/tmp/two"))] = 5
        bar: Annotated[str, Parameter(value_from=ValueFrom(path="/tmp/three"))] = "a default"
        baz: Annotated[str, Artifact(path="/tmp/four")]

    parameters = Foo._get_outputs(add_missing_path=True)

    assert parameters == [
        Parameter(name="foo", value_from=ValueFrom(path="/tmp/one")),
        Parameter(name="fum", default=5, value_from=ValueFrom(path="/tmp/two")),
        Parameter(name="bar", default="a default", value_from=ValueFrom(path="/tmp/three")),
        Artifact(name="baz", path="/tmp/four"),
    ]


def test_get_outputs_add_path_annotated_with_description():
    class Foo(Output):
        foo: Annotated[int, Parameter(description="param foo")]
        fum: Annotated[int, Parameter(description="param fum")] = 5
        bar: Annotated[str, Parameter(description="param bar")] = "a default"
        baz: Annotated[str, Artifact()]

    parameters = Foo._get_outputs(add_missing_path=True)

    assert parameters == [
        Parameter(name="foo", description="param foo", value_from=ValueFrom(path="/tmp/hera-outputs/parameters/foo")),
        Parameter(
            name="fum",
            description="param fum",
            default=5,
            value_from=ValueFrom(path="/tmp/hera-outputs/parameters/fum"),
        ),
        Parameter(
            name="bar",
            default="a default",
            description="param bar",
            value_from=ValueFrom(path="/tmp/hera-outputs/parameters/bar"),
        ),
        Artifact(name="baz", path="/tmp/hera-outputs/artifacts/baz"),
    ]


def test_get_outputs_add_path_with_multiple_annotations():
    class Foo(Output):
        foo: Annotated[int, Parameter(name="f_oo"), Field(gt=0)]
        fum: Annotated[int, Field(lt=10000), Parameter(name="f_um")] = 5
        bar: Annotated[str, Field(max_length=10), Parameter(description="param bar")] = "a default"
        baz: Annotated[str, Field(max_length=15), Artifact()]

    parameters = Foo._get_outputs(add_missing_path=True)

    assert parameters == [
        Parameter(name="f_oo", value_from=ValueFrom(path="/tmp/hera-outputs/parameters/f_oo")),
        Parameter(name="f_um", default=5, value_from=ValueFrom(path="/tmp/hera-outputs/parameters/f_um")),
        Parameter(
            name="bar",
            default="a default",
            description="param bar",
            value_from=ValueFrom(path="/tmp/hera-outputs/parameters/bar"),
        ),
        Artifact(name="baz", path="/tmp/hera-outputs/artifacts/baz"),
    ]


def test_get_as_invocator_output_unannotated():
    class Foo(Output):
        foo: int
        bar: str = "a default"

    foo = Foo.model_construct(foo="{{...foo}}", bar="{{...bar}}")
    parameters = foo._get_as_invocator_output()

    assert parameters == [
        Parameter(name="foo", value_from=ValueFrom(parameter="{{...foo}}")),
        Parameter(name="bar", value_from=ValueFrom(parameter="{{...bar}}")),
    ]


def test_get_as_invocator_output_with_pydantic_annotations():
    class Foo(Output):
        foo: Annotated[int, Field(gt=0)]
        bar: Annotated[str, Field(max_length=10)] = "a default"

    foo = Foo.model_construct(foo="{{...foo}}", bar="{{...bar}}")
    parameters = foo._get_as_invocator_output()

    assert parameters == [
        Parameter(name="foo", value_from=ValueFrom(parameter="{{...foo}}")),
        Parameter(name="bar", value_from=ValueFrom(parameter="{{...bar}}")),
    ]


def test_get_as_invocator_output_annotated_with_name():
    class Foo(Output):
        foo: Annotated[int, Parameter(name="f_oo")]
        bar: Annotated[str, Parameter(name="b_ar")] = "a default"
        baz: Annotated[str, Artifact(name="b_az")]

    foo = Foo.model_construct(foo="{{...foo}}", bar="{{...bar}}", baz="{{...baz}}")
    parameters = foo._get_as_invocator_output()

    assert parameters == [
        Parameter(name="f_oo", value_from=ValueFrom(parameter="{{...foo}}")),
        Parameter(name="b_ar", value_from=ValueFrom(parameter="{{...bar}}")),
        Artifact(name="b_az", from_="{{...baz}}"),
    ]


def test_get_as_invocator_output_annotated_with_description():
    class Foo(Output):
        foo: Annotated[int, Parameter(description="param foo")]
        bar: Annotated[str, Parameter(description="param bar")] = "a default"
        baz: Annotated[str, Artifact()]

    foo = Foo.model_construct(foo="{{...foo}}", bar="{{...bar}}", baz="{{...baz}}")
    parameters = foo._get_as_invocator_output()

    assert parameters == [
        Parameter(name="foo", description="param foo", value_from=ValueFrom(parameter="{{...foo}}")),
        Parameter(name="bar", description="param bar", value_from=ValueFrom(parameter="{{...bar}}")),
        Artifact(name="baz", from_="{{...baz}}"),
    ]


def test_get_as_invocator_output_with_multiple_annotations():
    class Foo(Output):
        foo: Annotated[int, Parameter(name="f_oo"), Field(gt=0)]
        bar: Annotated[str, Field(max_length=10), Parameter(description="param bar")] = "a default"
        baz: Annotated[str, Field(max_length=15), Artifact()]

    foo = Foo.model_construct(foo="{{...foo}}", bar="{{...bar}}", baz="{{...baz}}")
    parameters = foo._get_as_invocator_output()

    assert parameters == [
        Parameter(name="f_oo", value_from=ValueFrom(parameter="{{...foo}}")),
        Parameter(name="bar", description="param bar", value_from=ValueFrom(parameter="{{...bar}}")),
        Artifact(name="baz", from_="{{...baz}}"),
    ]
