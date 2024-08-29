"""Module that handles types and annotations."""

import sys
from typing import Any, Iterable, Optional, Tuple, Type, TypeVar, Union, overload

if sys.version_info >= (3, 9):
    from typing import Annotated, get_args, get_origin
else:
    # Python 3.8 has get_origin() and get_args() but those implementations aren't
    # Annotated-aware.
    from typing_extensions import Annotated, get_args, get_origin

if sys.version_info >= (3, 10):
    from types import UnionType
else:
    UnionType = Union


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
def get_annotated_metadata(annotation: Any, type_: Type[T]) -> Optional[T]: ...


@overload
def get_annotated_metadata(annotation: Any, type_: Tuple[Type[T], Type[V]]) -> Optional[Union[T, V]]: ...


# FIXME: Currently, mypy cannot guess following type hint properly: https://github.com/python/mypy/issues/17700
#        def get_annotated_metadata(_: Any, __: Union[Type[T], Tuple[Type[T], ...]]) -> Optional[T]: ...
#        Once fixed, remove overloads and add simpler type hints.
def get_annotated_metadata(annotation, type_):
    """If given annotation has metadata typed type_, return the metadata."""
    if not is_annotated(annotation):
        return None
    args = get_args(annotation)
    for arg in args[1:]:
        if isinstance(type_, Iterable):
            for t in type_:
                if isinstance(arg, t):
                    return arg
        else:
            if isinstance(arg, type_):
                return arg
    return None


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
