"""Module that handles types and annotations."""

from typing import Any, Iterable, Optional, Type, TypeAlias, TypeVar, Union, cast

try:
    from typing import Annotated, get_args, get_origin
except ImportError:
    from typing_extensions import Annotated, get_args, get_origin


def is_annotated(annotation: Any):
    """Check annotation has Annotated type or not."""
    return get_origin(annotation) is Annotated


_Types: TypeAlias = Union[type, tuple["_Types", ...]]


def has_annotated_metadata(annotation: Any, type_: _Types) -> bool:
    """If given annotation has metadata typed type_, return True."""
    args = get_args(annotation)
    for arg in args[1:]:
        if isinstance(arg, type_):
            return True
    return False


def consume_annotated_type(annotation: Any) -> type:
    """If the given type is annotated, return unsubscripted version. If not return itself."""
    if is_annotated(annotation):
        return get_args(annotation)[0]
    return annotation


T = TypeVar("T")


def consume_annotated_metadata(annotation: Any, type_: Union[Type[T], tuple[Type[T], ...]]) -> Optional[T]:
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
    if casted is Union:
        return any(can_consume_primitive(arg, target) for arg in get_args(annotation))
    return issubclass(casted, target)


def is_subscripted(t: type) -> bool:
    """Check if given type is subscripted."""
    return get_origin(t) is not None
