"""Module that handles types and annotations."""

import sys
from typing import (
    Annotated,
    Any,
    Iterable,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
    overload,
)

if sys.version_info >= (3, 10):
    from types import UnionType
else:
    UnionType = Union

from hera.workflows.artifact import Artifact
from hera.workflows.parameter import Parameter


def is_annotated(annotation: Any):
    """Check annotation has Annotated type or not."""
    return get_origin(annotation) is Annotated


def unwrap_annotation(annotation: Any) -> Any:
    """If the given annotation is of type Annotated, return the underlying type, otherwise return the annotation."""
    if is_annotated(annotation):
        return get_args(annotation)[0]
    return annotation


T = TypeVar("T")
V = TypeVar("V")


@overload
def get_annotated_metadata(annotation: Any, type_: Type[T]) -> List[T]: ...


@overload
def get_annotated_metadata(annotation: Any, type_: Tuple[Type[T], Type[V]]) -> List[Union[T, V]]: ...


def get_annotated_metadata(annotation, type_):
    """If given annotation has metadata typed type_, return the metadata.

    Prefer get_workflow_annotation if you want to call this with Artifact or Parameter.
    """
    if not is_annotated(annotation):
        return []

    found = []
    args = get_args(annotation)
    for arg in args[1:]:
        if isinstance(type_, Iterable):
            if any(isinstance(arg, t) for t in type_):
                found.append(arg)
        else:
            if isinstance(arg, type_):
                found.append(arg)
    return found


def get_workflow_annotation(annotation: Any) -> Optional[Union[Artifact, Parameter]]:
    """If given annotation has Artifact or Parameter metadata, return it.

    Note that this function will raise the error when multiple Artifact or Parameter metadata are given.
    """
    metadata = get_annotated_metadata(annotation, (Artifact, Parameter))
    if not metadata:
        return None
    if len(metadata) > 1:
        raise ValueError("Annotation metadata cannot contain more than one Artifact/Parameter.")
    return metadata[0]


def get_unsubscripted_type(t: Any) -> Any:
    """Return the origin of t, if subscripted, or t itself.

    This can be helpful if you want to use t with isinstance, issubclass, etc.,
    """
    if origin_type := get_origin(t):
        return origin_type
    return t


def origin_type_issubclass(cls: Any, type_: type) -> bool:
    """Return True if cls can be considered as a subclass of type_."""
    unwrapped_type = unwrap_annotation(cls)
    origin_type = get_unsubscripted_type(unwrapped_type)
    if origin_type is Union or origin_type is UnionType:
        return any(origin_type_issubclass(arg, type_) for arg in get_args(cls))
    return issubclass(origin_type, type_)


def is_subscripted(t: Any) -> bool:
    """Check if given type is subscripted, i.e. a typing object of the form X[Y, Z, ...].

    >>> is_subscripted(list[str])
    True
    >>> is_subscripted(str)
    False
    """
    return get_origin(t) is not None
