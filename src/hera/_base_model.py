from types import ModuleType
from typing import Optional

from pydantic import BaseModel as PyBaseModel
from pydantic import Extra

_yaml: Optional[ModuleType] = None
try:
    import yaml

    _yaml = yaml
except ImportError:
    _yaml = None


class BaseModel(PyBaseModel):
    class Config:
        allow_population_by_field_name = True
        extra = Extra.ignore
        allow_mutation = True
        use_enum_values = True
        arbitrary_types_allowed = True

    def to_yaml(self, **yaml_kwargs) -> str:
        """Returns a YAML representation of the object"""
        if _yaml is None:
            raise ImportError(
                "Attempted to use `to_yaml` but PyYAML is not available. "
                "Install `hera-workflows[yaml]` to install the extra dependency"
            )
        return _yaml.dump(self.dict(exclude_none=True, by_alias=True), **yaml_kwargs)


__all__ = ["BaseModel"]
