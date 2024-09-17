from typing import Annotated

from hera.shared import global_config
from hera.workflows import script

global_config.experimental_features["script_annotations"] = True


@script(constructor="runner")
def unknown_annotations_ignored(my_string: Annotated[str, "some metadata"]) -> str:
    return my_string
