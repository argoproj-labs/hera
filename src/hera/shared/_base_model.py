from typing import TypeVar

from pydantic import BaseModel as PyBaseModel

TBase = TypeVar("TBase", bound="BaseMixin")


class BaseModel(PyBaseModel):
    class Config:
        allow_population_by_field_name = True
        allow_mutation = True
        use_enum_values = True
        arbitrary_types_allowed = True
        smart_union = True


class BaseMixin(BaseModel):
    # Note this is pydantic private method that
    # is called after __init__
    # In order to inject __hera_init__ after __init__
    # without destroying the autocomplete, we have opted
    # for this method. We also tried other ways
    # including creating a metaclass that invokes hera_init
    # after init, but that always broke auto-complete for vscode
    def _init_private_attributes(self):
        super()._init_private_attributes()
        self.__hera_init__()

    def __hera_init__(self):
        ...
