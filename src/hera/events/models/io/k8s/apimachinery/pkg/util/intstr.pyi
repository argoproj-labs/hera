from hera.shared._pydantic import BaseModel as BaseModel

class IntOrString(BaseModel):
    __root__: str
