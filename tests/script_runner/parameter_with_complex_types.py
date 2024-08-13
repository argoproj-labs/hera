import sys
from typing import Optional, Union

from hera.shared import global_config
from hera.workflows import script

global_config.experimental_features["script_annotations"] = True


@script(constructor="runner")
def optional_str_parameter(my_string: Optional[str]) -> Optional[str]:
    return my_string


@script(constructor="runner")
def optional_str_parameter_using_union(my_string: Union[None, str]) -> Union[None, str]:
    return my_string


if sys.version_info[0] >= 3 and sys.version_info[1] >= 10:
    # Union types using OR operator are allowed since python 3.10.
    @script(constructor="runner")
    def optional_str_parameter_using_or(my_string: str | None) -> str | None:
        return my_string


@script(constructor="runner")
def optional_int_parameter(my_int: Optional[int]) -> Optional[int]:
    return my_int


@script(constructor="runner")
def union_parameter(my_param: Union[str, int]) -> Union[str, int]:
    return my_param
