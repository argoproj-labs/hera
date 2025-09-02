"""Module that handles types and annotations."""

import sys
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    Iterable,
    List,
    Literal,
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
    from types import NoneType, UnionType
else:
    UnionType = Union
    NoneType = type(None)

if TYPE_CHECKING:
    # Avoid circular import
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


def get_workflow_annotation(annotation: Any) -> "Optional[Union[Artifact, Parameter]]":
    """If given annotation has Artifact or Parameter metadata, return it.

    Note that this function will raise the error when multiple Artifact or Parameter metadata are given.
    """
    from hera.workflows.artifact import Artifact
    from hera.workflows.parameter import Parameter

    metadata = get_annotated_metadata(annotation, (Artifact, Parameter))
    if not metadata:
        return None
    if len(metadata) > 1:
        raise ValueError("Annotation metadata cannot contain more than one Artifact/Parameter.")
    return metadata[0]


def set_enum_based_on_type(parameter: "Parameter", annotation: Any) -> None:
    """Sets the enum field of a Parameter based on its type annotation.

    Currently, only supports Literals.
    """
    if parameter.enum:
        return
    type_ = unwrap_annotation(annotation)
    if get_origin(type_) is Literal:
        parameter.enum = list(get_args(type_))


def construct_io_from_annotation(python_name: str, annotation: Any) -> "Union[Parameter, Artifact]":
    """Constructs a Parameter or Artifact object based on annotations.

    If a field has a Parameter or Artifact annotation, a copy will be returned, with missing
    fields filled out based on other metadata. Otherwise, a Parameter object will be constructed.

    For a function parameter, python_name should be the parameter name.
    For a Pydantic Input or Output class, python_name should be the field name.
    """
    from hera.workflows.parameter import Parameter

    if workflow_annotation := get_workflow_annotation(annotation):
        # Copy so as to not modify the fields themselves
        io = workflow_annotation.copy()
    else:
        io = Parameter()

    io.name = io.name or python_name
    if isinstance(io, Parameter):
        set_enum_based_on_type(io, annotation)
    else:  # isinstance(io, Artifact)
        is_optional_annotation = origin_type_issupertype(annotation, NoneType)
        if io.optional is True and not is_optional_annotation:
            # Assume user wants optional
            raise ValueError("Artifact annotation must be `Optional` for optional Artifacts.")

        if is_optional_annotation and io.optional is False:
            raise ValueError("Artifact annotation does not match Artifact.optional.")

        if is_optional_annotation:
            io.optional = True

    return io


def get_unsubscripted_type(t: Any) -> Any:
    """Return the origin of t, if subscripted, or t itself.

    This can be helpful if you want to use t with isinstance, issubclass, etc.,
    """
    if origin_type := get_origin(t):
        return origin_type
    return t


def origin_type_issubtype(annotation: Any, type_: Union[type, Tuple[type, ...]]) -> bool:
    """Return True if annotation is a subtype of type_.

    type_ may be a tuple of types, in which case return True if annotation is a subtype
    of the union of the types in the tuple.
    """
    unwrapped_type = unwrap_annotation(annotation)
    origin_type = get_unsubscripted_type(unwrapped_type)
    if origin_type is Union or origin_type is UnionType:
        return all(origin_type_issubtype(arg, type_) for arg in get_args(unwrapped_type))
    if origin_type is Literal:
        return all(isinstance(value, type_) for value in get_args(unwrapped_type))
    return isinstance(origin_type, type) and issubclass(origin_type, type_)


def origin_type_issupertype(annotation: Any, type_: type) -> bool:
    """Return True if annotation is a supertype of type_.

    Useful for checking if annotation is an optional type:

    >>> origin_type_issupertype(Optional[str], NoneType)
    True
    """
    unwrapped_type = unwrap_annotation(annotation)
    origin_type = get_unsubscripted_type(unwrapped_type)
    if origin_type is Union or origin_type is UnionType:
        return any(origin_type_issupertype(arg, type_) for arg in get_args(unwrapped_type))
    return isinstance(origin_type, type) and issubclass(type_, origin_type)


def is_subscripted(t: Any) -> bool:
    """Check if given type is subscripted, i.e. a typing object of the form X[Y, Z, ...].

    >>> is_subscripted(list[str])
    True
    >>> is_subscripted(str)
    False
    """
    return get_origin(t) is not None
