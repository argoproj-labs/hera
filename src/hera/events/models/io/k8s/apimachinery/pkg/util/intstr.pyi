from typing import Union

from hera.shared._pydantic import BaseModel as BaseModel

class IntOrString(BaseModel):
    __root__: Union[str, int]
