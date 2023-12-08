from hera.shared._pydantic import (
    BaseModel as BaseModel,
    Field as Field,
)

class Quantity(BaseModel):
    __root__: str
