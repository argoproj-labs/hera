from typing import List, Optional, Union

import pytest
from annotated_types import Gt

from hera.shared._type_util import (
    get_annotated_metadata,
    get_unsubscripted_type,
    get_workflow_annotation,
    is_annotated,
    origin_type_issubclass,
    unwrap_annotation,
)
from hera.workflows import Artifact, Parameter

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated


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
        [List[str], list],
        [Optional[str], Union],
    ],
)
def test_get_unsubscripted_type(annotation, expected):
    assert get_unsubscripted_type(annotation) is expected


@pytest.mark.parametrize(
    "annotation, target, expected",
    [
        [List[str], str, False],
        [Optional[str], str, True],
        [str, str, True],
        [Union[int, str], int, True],
    ],
)
def test_origin_type_issubclass(annotation, target, expected):
    assert origin_type_issubclass(annotation, target) is expected
