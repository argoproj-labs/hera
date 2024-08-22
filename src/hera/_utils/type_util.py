"""Module that handles types and annotations."""

from typing import Any, Iterable, Optional, Tuple, Type, TypeVar, Union, cast, overload

try:
    from types import UnionType  # type: ignore
except ImportError:
    UnionType = Union  # type: ignore

try:
    from typing import Annotated, get_args, get_origin  # type: ignore
except ImportError:
    from typing_extensions import Annotated, get_args, get_origin  # type: ignore


def is_annotated(annotation: Any):
    """Check annotation has Annotated type or not."""
    return get_origin(annotation) is Annotated


def consume_annotated_type(annotation: Any) -> type:
    """If the given type is annotated, return unsubscripted version. If not return itself."""
    if is_annotated(annotation):
        return get_args(annotation)[0]
    return annotation


T = TypeVar("T")
V = TypeVar("V")


@overload
def consume_annotated_metadata(_: Any, __: Type[T]) -> Optional[T]: ...


@overload
def consume_annotated_metadata(_: Any, __: Tuple[Type[T], Type[V]]) -> Optional[Union[T, V]]: ...


# FIXME: Currently, mypy cannot guess following type hint properly: https://github.com/python/mypy/issues/17700
#        def consume_annotated_metadata(_: Any, __: Union[Type[T], Tuple[Type[T], ...]]) -> Optional[T]: ...
#        Once fixed, remove overloads and add simpler type hints.
def consume_annotated_metadata(annotation, type_):
    """If given annotation has metadata typed type_, return the metadata."""
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


def may_cast_subscripted_type(t: type) -> type:
    """If the given type is subscripted, cast and return it.

    This can be helpful if you want to use t with isinstance, issubclass, or etc.,
    """
    if origin_type := get_origin(t):
        return cast(type, origin_type)
    return t


def can_consume_primitive(annotation: type, target: type) -> bool:
    """If annotation can be considered as target type or subclass of it, return True."""
    if is_annotated(annotation):
        annotation = consume_annotated_type(annotation)
    casted = may_cast_subscripted_type(annotation)
    if casted is Union or casted is UnionType:
        return any(can_consume_primitive(arg, target) for arg in get_args(annotation))
    return issubclass(casted, target)


def is_subscripted(t: type) -> bool:
    """Check if given type is subscripted."""
    return get_origin(t) is not None
