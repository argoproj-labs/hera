import json
from typing import Union, Dict, List

from pydantic import BaseModel


JSONType = Union[None, BaseModel, bool, str, float, int, List['JSONType'], Dict[str, 'JSONType']]  # type: ignore


def encode_json(value: JSONType) -> str:
    if isinstance(value, BaseModel):
        return value.json()
    elif isinstance(value, str):
        return value
    else:
        return json.dumps(value)


def create_param_extraction(param_name: str) -> str:
    return f"""
try:
    {param_name} = json.loads('''{{{{inputs.parameters.{param_name}}}}}''')
except json.JSONDecodeError:
    # Edge case for when parameter is a bare string
    {param_name} = '{{{{inputs.parameters.{param_name}}}}}'
"""
