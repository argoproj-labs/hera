from typing import List, Optional, Union

import pytest

from hera._utils import type_util
from hera.workflows import Artifact, Parameter

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated


@pytest.mark.parametrize("annotation, expected", [[Annotated[str, "some metadata"], True], [str, False]])
def test_is_annotated(annotation, expected):
    assert type_util.is_annotated(annotation) == expected


@pytest.mark.parametrize(
    "annotation, t, expected",
    [
        [Annotated[str, Parameter(name="a_str")], Parameter, True],
        [Annotated[str, "some metadata"], Parameter, False],
        # Must support variadic annotated
        [Annotated[str, "some metadata", Parameter(name="a_str")], Parameter, True],
        # Must support tuple of types
        [Annotated[str, "some metadata", Parameter(name="a_str")], (Parameter, Artifact), True],
    ],
)
def test_has_annotated_metadata(annotation, t, expected):
    assert type_util.has_annotated_metadata(annotation, t) == expected


@pytest.mark.parametrize(
    "annotation, expected",
    [
        [Annotated[str, Parameter(name="a_str")], str],
        [Annotated[str, "some metadata"], str],
        [str, str],
    ],
)
def test_consume_annotated_type(annotation, expected):
    assert type_util.consume_annotated_type(annotation) == expected


@pytest.mark.parametrize(
    "annotation, t, expected",
    [
        [Annotated[str, Parameter(name="a_str")], Parameter, Parameter(name="a_str")],
        [Annotated[str, "some metadata"], Parameter, None],
        # Must support variadic annotated
        [Annotated[str, "some metadata", Parameter(name="a_str")], Parameter, Parameter(name="a_str")],
        # Must support multiple types
        [Annotated[str, "some metadata", Parameter(name="a_str")], (Parameter, Artifact), Parameter(name="a_str")],
        # Must consume in order
        [
            Annotated[str, "some metadata", Artifact(name="a_str"), Parameter(name="a_str")],
            (Parameter, Artifact),
            Artifact(name="a_str"),
        ],
    ],
)
def test_consume_annotated_metadata(annotation, t, expected):
    assert type_util.consume_annotated_metadata(annotation, t) == expected


@pytest.mark.parametrize(
    "annotation, expected",
    [
        [List[str], list],
        [Optional[str], Union],
    ],
)
def test_may_cast_subscripted_type(annotation, expected):
    assert type_util.may_cast_subscripted_type(annotation) is expected


@pytest.mark.parametrize(
    "annotation, target, expected",
    [
        [list[str], str, False],
        [Optional[str], str, True],
        [str, str, True],
        [Union[int, str], int, True],
    ],
)
def test_can_consume_primitive(annotation, target, expected):
    assert type_util.can_consume_primitive(annotation, target) is expected
