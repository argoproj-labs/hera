from pydantic import BaseModel as PyBaseModel


class BaseModel(PyBaseModel):
    class Config:
        allow_population_by_field_name = True
        allow_mutation = True
        use_enum_values = True
        arbitrary_types_allowed = True
        smart_union = True
