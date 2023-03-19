import json
from typing import Any

MISSING = object()


def serialize(value: Any):
    if value is MISSING:
        return None
    elif isinstance(value, str):
        return value
    else:
        return json.dumps(value)  # None serialized as `null`
