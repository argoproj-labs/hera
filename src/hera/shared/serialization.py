"""A serialization module that contains utilities for serializing any values passed to the Argo server via Hera."""

import json
from json import JSONEncoder
from typing import Any, Optional

from pydantic import BaseModel

# NOTE: Use the original BaseModel in order to support serializing user-defined models,
# for hera internal models, we still need to support v1 base models.
from pydantic.v1 import BaseModel as V1BaseModel

MISSING = object()
"""`MISSING` is a placeholder that indicates field value nullity.

When the user of a Hera object sets the field of an object specifically to `None`, Hera needs to distinguish between
default nullity/None and user-provided `None` on, say, something like the `source` of `Script`.
"""


class PydanticEncoder(JSONEncoder):
    """Default serializer of Hera objects."""

    def default(self, o: Any):
        """Return the default representation of the given object."""
        # Note that these are slightly different outputs b/w v1 and v2
        # v1 will give the actual python object whereas v2 will serialize it into
        # a json compatible format.
        if isinstance(o, V1BaseModel):
            return o.dict(by_alias=True)
        if isinstance(o, BaseModel):
            return o.model_dump(by_alias=True, mode="json")  # type: ignore
        return super().default(o)


def serialize(value: Any) -> Optional[str]:
    """Serialize the given value.

    If the value is `MISSING` then a proper `None` is returned. Since strings are "serialized" already, they are simply
    returned. Everything else is JSON encoded and returned.
    """
    if value == MISSING:
        return None
    elif isinstance(value, str):
        return value
    else:
        return json.dumps(value, cls=PydanticEncoder)  # None serialized as `null`
