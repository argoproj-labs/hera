from typing import Optional

from hera.shared._pydantic import BaseModel as BaseModel

class Any(BaseModel):
    type_url: Optional[str]
    value: Optional[str]
