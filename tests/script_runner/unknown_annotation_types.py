from typing import Annotated

from hera.workflows import script


@script(constructor="runner")
def unknown_annotations_ignored(my_string: Annotated[str, "some metadata"]) -> str:
    return my_string
