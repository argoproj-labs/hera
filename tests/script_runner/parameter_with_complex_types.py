import sys
from typing import Optional, Tuple, Union

if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated

from hera.shared import global_config
from hera.workflows import Parameter, script

global_config.experimental_features["script_annotations"] = True


@script(constructor="runner")
def optional_str_parameter(my_string: Optional[str] = None) -> Optional[str]:
    return my_string


@script(constructor="runner")
def optional_str_parameter_using_union(my_string: Union[None, str] = None) -> Union[None, str]:
    return my_string


if sys.version_info[0] >= 3 and sys.version_info[1] >= 10:
    # Union types using OR operator are allowed since python 3.10.
    @script(constructor="runner")
    def optional_str_parameter_using_or(my_string: str | None = None) -> str | None:
        return my_string

    @script(constructor="runner")
    def optional_str_parameter_using_multiple_or(my_string: str | int | None = None) -> str:
        return my_string


@script(constructor="runner")
def optional_int_parameter(my_int: Optional[int] = None) -> Optional[int]:
    return my_int


@script(constructor="runner")
def union_parameter(my_param: Union[str, int] = None) -> Union[str, int]:
    return my_param


@script(constructor="runner")
def fn_with_output_tuple(my_string: str) -> Tuple[str, str]:
    return my_string, my_string


@script(constructor="runner")
def fn_with_output_tuple_partially_annotated(my_string: str) -> Tuple[str, Annotated[str, Parameter(name="sample")]]:
    return my_string, my_string
