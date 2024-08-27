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
    "annotation, expected",
    [
        [Annotated[str, Parameter(name="a_str")], str],
        [Annotated[str, "some metadata"], str],
        [str, str],
    ],
)
def test_unwrap_annotation(annotation, expected):
    assert type_util.unwrap_annotation(annotation) == expected


@pytest.mark.parametrize(
    "annotation, t, expected",
    [
        # Not annotated one.
        [str, Parameter, None],
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
def test_get_annotated_metadata(annotation, t, expected):
    assert type_util.get_annotated_metadata(annotation, t) == expected


@pytest.mark.parametrize(
    "annotation, expected",
    [
        [List[str], list],
        [Optional[str], Union],
    ],
)
def test_get_origin_or_builtin(annotation, expected):
    assert type_util.get_origin_or_builtin(annotation) is expected


@pytest.mark.parametrize(
    "annotation, target, expected",
    [
        [List[str], str, False],
        [Optional[str], str, True],
        [str, str, True],
        [Union[int, str], int, True],
    ],
)
def test_can_consume_primitive(annotation, target, expected):
    assert type_util.can_consume_primitive(annotation, target) is expected
