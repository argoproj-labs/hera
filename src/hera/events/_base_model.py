from types import ModuleType
from typing import Any, Optional

from pydantic import (
    BaseModel as PyBaseModel,
    Extra,
)
from pydantic.main import ModelMetaclass as _PyModelMetaclass

_yaml: Optional[ModuleType] = None
try:
    import yaml

    _yaml = yaml
except ImportError:
    _yaml = None


class ModelMetaclass(_PyModelMetaclass):
    def __call__(cls, *args, **kwargs):
        obj = type.__call__(cls, *args, **kwargs)
        if hasattr(obj, "__post_init__"):
            return obj.__post_init__()
        return obj


class BaseModel(PyBaseModel, metaclass=ModelMetaclass):
    class Config:
        allow_population_by_field_name = True
        extra = Extra.ignore
        allow_mutation = True
        use_enum_values = True
        arbitrary_types_allowed = True
        smart_union = True

    def to_dict(self) -> Any:
        return self.dict(exclude_none=True, by_alias=True)

    def to_yaml(self, **yaml_kwargs) -> str:
        """Returns a YAML representation of the object"""
        if _yaml is None:
            raise ImportError(
                "Attempted to use `to_yaml` but PyYAML is not available. "
                "Install `hera-workflows[yaml]` to install the extra dependency"
            )
        return _yaml.dump(self.to_dict(), **yaml_kwargs)


__all__ = ["BaseModel"]
