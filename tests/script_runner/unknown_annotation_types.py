try:
    from typing import Annotated  # type: ignore
except ImportError:
    from typing_extensions import Annotated  # type: ignore


from hera.shared import global_config
from hera.workflows import script

global_config.experimental_features["script_annotations"] = True
global_config.experimental_features["script_runner"] = True


@script(constructor="runner")
def unknown_annotations_ignored(my_string: Annotated[str, "some metadata"]) -> str:
    return my_string
