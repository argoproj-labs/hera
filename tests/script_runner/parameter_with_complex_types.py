from typing import Annotated, Optional, Tuple, Union

from hera.workflows import Parameter, script


@script(constructor="runner")
def optional_str_parameter(my_string: Optional[str] = None) -> Optional[str]:
    return my_string


@script(constructor="runner")
def optional_str_parameter_using_union(my_string: Union[None, str] = None) -> Union[None, str]:
    return my_string


# Union types using OR operator are allowed since python 3.10.
@script(constructor="runner")
def optional_str_parameter_using_or(my_string: str | None = None) -> str | None:
    return my_string


@script(constructor="runner")
def optional_str_parameter_using_multiple_or(my_string: str | int | None = None) -> str | int | None:
    return my_string


@script(constructor="runner")
def optional_int_parameter(my_int: Optional[int] = None) -> Optional[int]:
    return my_int


@script(constructor="runner")
def union_parameter(my_param: Union[str, int] = "") -> Union[str, int]:
    return my_param


@script(constructor="runner")
def fn_with_output_tuple(my_string: str) -> Tuple[str, str]:
    return my_string, my_string


@script(constructor="runner")
def fn_with_output_tuple_partially_annotated(my_string: str) -> Tuple[str, Annotated[str, Parameter(name="sample")]]:
    return my_string, my_string
