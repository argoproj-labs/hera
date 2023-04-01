import json
from json import JSONEncoder
from typing import Any

from pydantic import BaseModel

MISSING = object()


class PydanticEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, BaseModel):
            return o.dict(by_alias=True)
        return super().default(o)


def serialize(value: Any):
    if value == MISSING:
        return None
    elif isinstance(value, str):
        return value
    else:
        return json.dumps(value, cls=PydanticEncoder)  # None serialized as `null`
