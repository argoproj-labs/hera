"""A serialization module that contains utilities for serializing any values passed to the Argo server via Hera."""
import json
from json import JSONEncoder
from typing import Any, Optional

# NOTE: Use the original BaseModel in order to support serializing user-defined models,
# which won't use our hera.shared._pydantic import. This does still require that the
# user-defined models are using v1 pydantic models for now (either from a pydantic v1
# installation or `pydantic.v1` import from a pydantic v2 installation).
from hera.shared._pydantic import PydanticBaseModel

MISSING = object()
"""`MISSING` is a placeholder that indicates field value nullity.

When the user of a Hera object sets the field of an object specifically to `None`, Hera needs to distinguish between
default nullity/None and user-provided `None` on, say, something like the `source` of `Script`.
"""


class PydanticEncoder(JSONEncoder):
    """Default serializer of Hera objects."""

    def default(self, o: Any):
        """Return the default representation of the given object."""
        if isinstance(o, PydanticBaseModel):
            return o.dict(by_alias=True)
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
