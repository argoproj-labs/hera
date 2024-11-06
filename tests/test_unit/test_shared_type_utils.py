import sys
from typing import List, Literal, NoReturn, Optional, Union

if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated
if sys.version_info >= (3, 10):
    from types import NoneType
else:
    NoneType = type(None)

import pytest
from annotated_types import Gt

from hera.shared._type_util import (
    construct_io_from_annotation,
    get_annotated_metadata,
    get_unsubscripted_type,
    get_workflow_annotation,
    is_annotated,
    origin_type_issubtype,
    origin_type_issupertype,
    unwrap_annotation,
)
from hera.workflows import Artifact, Parameter


@pytest.mark.parametrize("annotation, expected", [[Annotated[str, "some metadata"], True], [str, False]])
def test_is_annotated(annotation, expected):
    assert is_annotated(annotation) == expected


@pytest.mark.parametrize(
    "annotation, expected",
    [
        [Annotated[str, Parameter(name="a_str")], str],
        [Annotated[str, "some metadata"], str],
        [str, str],
    ],
)
def test_unwrap_annotation(annotation, expected):
    assert unwrap_annotation(annotation) == expected


@pytest.mark.parametrize(
    "annotation, t, expected",
    [
        # Not annotated one.
        [str, Parameter, []],
        [Annotated[str, Parameter(name="a_str")], Parameter, [Parameter(name="a_str")]],
        [Annotated[str, "some metadata"], Parameter, []],
        # Must support variadic annotated
        [Annotated[str, "some metadata", Parameter(name="a_str")], Parameter, [Parameter(name="a_str")]],
        # Must support multiple types
        [Annotated[str, "some metadata", Parameter(name="a_str")], (Parameter, Artifact), [Parameter(name="a_str")]],
        # Must consume in order
        [
            Annotated[str, "some metadata", Artifact(name="a_str"), Parameter(name="a_str")],
            (Parameter, Artifact),
            [Artifact(name="a_str"), Parameter(name="a_str")],
        ],
    ],
)
def test_get_annotated_metadata(annotation, t, expected):
    assert get_annotated_metadata(annotation, t) == expected


@pytest.mark.parametrize(
    "annotation, expected",
    [
        [str, None],
        [Annotated[str, Parameter(name="a_str")], Parameter(name="a_str")],
        [Annotated[str, Artifact(name="a_str")], Artifact(name="a_str")],
        [Annotated[int, Gt(10), Artifact(name="a_int")], Artifact(name="a_int")],
        [Annotated[int, Artifact(name="a_int"), Gt(30)], Artifact(name="a_int")],
        # this can happen when user uses already annotated types.
        [Annotated[Annotated[int, Gt(10)], Artifact(name="a_int")], Artifact(name="a_int")],
    ],
)
def test_get_workflow_annotation(annotation, expected):
    assert get_workflow_annotation(annotation) == expected


@pytest.mark.parametrize(
    "annotation",
    [
        # Duplicated annotation
        Annotated[str, Parameter(name="a_str"), Parameter(name="b_str")],
        Annotated[str, Parameter(name="a_str"), Artifact(name="a_str")],
        # Nested
        Annotated[Annotated[str, Parameter(name="a_str")], Artifact(name="b_str")],
    ],
)
def test_get_workflow_annotation_should_raise_error(annotation):
    with pytest.raises(ValueError):
        get_workflow_annotation(annotation)


@pytest.mark.parametrize(
    "annotation, expected",
    [
        [str, Parameter(name="python_name")],
        [Annotated[str, Parameter(name="a_str")], Parameter(name="a_str")],
        [Annotated[str, Artifact(name="a_str")], Artifact(name="a_str")],
        [Annotated[int, Gt(10), Artifact(name="a_int")], Artifact(name="a_int")],
        [Annotated[int, Artifact(name="a_int"), Gt(30)], Artifact(name="a_int")],
        # this can happen when user uses already annotated types.
        [Annotated[Annotated[int, Gt(10)], Artifact(name="a_int")], Artifact(name="a_int")],
    ],
)
def test_construct_io_from_annotation(annotation, expected):
    assert construct_io_from_annotation("python_name", annotation) == expected


@pytest.mark.parametrize(
    "annotation",
    [
        # Duplicated annotation
        Annotated[str, Parameter(name="a_str"), Parameter(name="b_str")],
        Annotated[str, Parameter(name="a_str"), Artifact(name="a_str")],
        # Nested
        Annotated[Annotated[str, Parameter(name="a_str")], Artifact(name="b_str")],
    ],
)
def test_construct_io_from_annotation_should_raise_error(annotation):
    with pytest.raises(ValueError):
        construct_io_from_annotation("python_name", annotation)


@pytest.mark.parametrize(
    "annotation, expected",
    [
        [List[str], list],
        [Optional[str], Union],
    ],
)
def test_get_unsubscripted_type(annotation, expected):
    assert get_unsubscripted_type(annotation) is expected


@pytest.mark.parametrize(
    "annotation, target, expected",
    [
        pytest.param(List[str], str, False, id="list-str-not-subtype-of-str"),
        pytest.param(NoReturn, str, False, id="special-form-does-not-raise-error"),
        pytest.param(Optional[str], str, False, id="optional-str-not-subtype-of-str"),
        pytest.param(str, str, True, id="str-is-subtype-of-str"),
        pytest.param(Union[int, str], int, False, id="union-int-str-not-subtype-of-str"),
        pytest.param(Optional[str], (str, NoneType), True, id="optional-str-is-subtype-of-optional-str"),
        pytest.param(Annotated[Optional[str], "foo"], (str, NoneType), True, id="annotated-optional"),
        pytest.param(str, (str, NoneType), True, id="str-is-subtype-of-optional-str"),
        pytest.param(Union[int, str], (str, NoneType), False, id="union-int-str-not-subtype-of-optional-str"),
        pytest.param(Literal["foo", "bar"], (str, NoneType), True, id="literal-str-is-subtype-of-optional-str"),
        pytest.param(Literal["foo", None], (str, NoneType), True, id="literal-none-is-subtype-of-optional-str"),
        pytest.param(Literal[1, 2], (str, NoneType), False, id="literal-int-not-subtype-of-optional-str"),
        pytest.param(Literal[1, "foo"], (str, NoneType), False, id="mixed-literal-not-subtype-of-optional-str"),
    ],
)
def test_origin_type_issubtype(annotation, target, expected):
    assert origin_type_issubtype(annotation, target) is expected


@pytest.mark.parametrize(
    "annotation, target, expected",
    [
        pytest.param(List[str], str, False, id="list-str-not-supertype-of-str"),
        pytest.param(NoReturn, str, False, id="special-form-does-not-raise-error"),
        pytest.param(Optional[str], str, True, id="optional-str-is-supertype-of-str"),
        pytest.param(str, str, True, id="str-is-supertype-of-str"),
        pytest.param(Union[int, str], int, True, id="union-int-str-is-supertype-of-int"),
        pytest.param(Optional[str], NoneType, True, id="optional-str-is-supertype-of-nonetype"),
        pytest.param(Annotated[Optional[str], "foo"], NoneType, True, id="annotated-optional"),
        pytest.param(str, NoneType, False, id="str-not-supertype-of-nonetype"),
    ],
)
def test_origin_type_issupertype(annotation, target, expected):
    assert origin_type_issupertype(annotation, target) is expected
