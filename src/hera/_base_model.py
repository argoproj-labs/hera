from types import ModuleType
from typing import Optional

from pydantic import BaseModel, Extra

_yaml: Optional[ModuleType] = None
try:
    import yaml

    _yaml = yaml
except ImportError:
    _yaml = None


class ArgoBaseModel(BaseModel):
    class Config:
        allow_population_by_field_name = True
        extra = Extra.forbid
        allow_mutation = True
        use_enum_values = True

    def to_yaml(self, **yaml_kwargs) -> str:
        """Returns a YAML representation of the object"""
        if _yaml is None:
            raise ImportError(
                "Attempted to use `to_yaml` but PyYAML is not available. "
                "Install `hera-workflows[yaml]` to install the extra dependency"
            )
        return _yaml.dump(self.dict(exclude_none=True, by_alias=True), **yaml_kwargs)
