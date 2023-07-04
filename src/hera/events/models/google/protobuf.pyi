from hera.shared._base_model import BaseModel as BaseModel
from typing import Optional

class Any(BaseModel):
    type_url: Optional[str]
    value: Optional[str]
