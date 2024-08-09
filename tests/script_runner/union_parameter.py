try:
    from typing import Union  # type: ignore
except ImportError:
    from typing_extensions import Union  # type: ignore


from hera.shared import global_config
from hera.workflows import script

global_config.experimental_features["script_annotations"] = True


@script(constructor="runner")
def union_parameter(my_param: Union[str, int]) -> Union[str, int]:
    return my_param
