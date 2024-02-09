"""Define the base classes used to produce k8s CRDs."""
from __future__ import annotations

from collections import ChainMap
from typing import Any, Callable, ClassVar, Dict, List, Optional, Type, Union

try:
    from inspect import get_annotations  # type: ignore
except ImportError:
    from hera.workflows._inspect import get_annotations  # type: ignore
from pathlib import Path

try:
    from typing import Annotated, get_args, get_origin  # type: ignore
except ImportError:
    from typing_extensions import Annotated, get_args, get_origin  # type: ignore

try:
    from typing import Self  # type: ignore
except ImportError:
    from typing_extensions import Self  # type: ignore

from hera import _yaml
from hera.shared import BaseMixin
from hera.shared._pydantic import PydanticBaseModel, get_fields


class ModelMapper:
    """Maps a model attribute to the attribute path of the produced resource.

    For example `foo: ModelMapper("metadata.name")` would map the annotated object's
    `foo` attribute to the "metadata" -> "name" field on the final k8s resource.
    """

    def __init__(self, model_path: str, hera_builder: Optional[Callable] = None):
        """Accept the `model_path` to map to."""
        self.model_path = None
        self.builder = hera_builder

        if not model_path:
            # Allows overriding parent attribute annotations to remove the mapping
            return

        self.model_path = model_path.split(".")

    @classmethod
    def build_model(
        cls,
        hera_class: Type[ResourceBase],
        hera_obj: ResourceBase,
        model: PydanticBaseModel,
        *,
        traverse_mro: bool = True,
    ):
        """Builds an instance of a `ResourceBase` into the destination model type."""
        assert isinstance(hera_obj, ResourceBase), type(hera_obj)

        for attr, mapper, _ in hera_class._iter_model_mappers(traverse_mro=traverse_mro):
            # Value comes from builder function if it exists on hera_obj, otherwise directly from the attr
            value = (
                getattr(hera_obj, mapper.builder.__name__)() if mapper.builder is not None else getattr(hera_obj, attr)
            )
            if value is not None:
                _set_model_attr(model, mapper.model_path, value)

        return model


class ResourceBase(BaseMixin):
    """Base class for top-level Hera CRDs.

    Subclasses should supply a `mapped_model` attribute, which is the Pydantic model
    which represents the final k8s resource.

    Note, this class will validate that the annotated attributes map to real fields on the `mapped_model`.
    """

    mapped_model: ClassVar[Type[PydanticBaseModel]]

    def __init_subclass__(cls, *, traverse_mro=True, **kwargs):
        """Validate that the annotated `ModelMapper` paths map to real destination fields."""
        for _, model_mapper, _ in cls._iter_model_mappers(traverse_mro=traverse_mro):
            try:
                curr_cls = cls.mapped_model
            except AttributeError:
                raise AttributeError(
                    f"{cls.__qualname__} must define a `mapped_model` attribute, "
                    "which specifies the Pydantic model to which this resource's attributes map."
                )

            for key in model_mapper.model_path:
                fields = get_fields(curr_cls)
                if key not in fields:
                    raise ValueError(f"Model key '{key}' does not exist in class {curr_cls.__qualname__}")
                curr_cls = fields[key].outer_type_

        super().__init_subclass__(**kwargs)

    @classmethod
    def _iter_model_mappers(cls, traverse_mro: bool = True):
        mro = cls.__mro__
        if not traverse_mro:
            mro = (cls,)

        # Due to child subclasses being able to override parent fields, ChainMap over the mro order
        # yields only leaf instances of each attribute.
        annotations = ChainMap(*({k: (v, c) for k, v in get_annotations(c).items()} for c in mro))

        for attr, (annotation, c) in annotations.items():
            if get_origin(annotation) is Annotated and isinstance(get_args(annotation)[1], ModelMapper):
                model_mapper = get_args(annotation)[1]

                if not model_mapper.model_path:
                    continue

                yield attr, model_mapper, c

    def build(self) -> PydanticBaseModel:
        """Builds the Workflow as an Argo schema Workflow object."""
        raise NotImplementedError()

    def to_dict(self) -> dict:
        """Builds the Workflow as an Argo schema Workflow object and returns it as a dictionary."""
        return self.build().dict(exclude_none=True, by_alias=True)

    def to_yaml(self, *args, **kwargs) -> str:
        """Builds the Workflow as an Argo schema Workflow object and returns it as yaml string."""
        return _yaml.dump(self.to_dict(), *args, **kwargs)

    @classmethod
    def _from_model(cls, model: PydanticBaseModel) -> Self:
        """Parse from given model to cls's type."""
        hera_obj = cls()

        for attr, mapper, _ in cls._iter_model_mappers():
            value = _get_model_attr(model, mapper.model_path)
            if value is not None:
                setattr(hera_obj, attr, value)

        return hera_obj

    @classmethod
    def _from_dict(cls, model_dict: Dict, model: Type[PydanticBaseModel]) -> Self:
        """Parse from given model_dict, using the given model type to call its parse_obj."""
        model_workflow = model.parse_obj(model_dict)
        return cls._from_model(model_workflow)

    @classmethod
    def from_dict(cls, model_dict: Dict) -> Self:
        """Parse from given model_dict."""
        raise NotImplementedError

    @classmethod
    def _from_yaml(cls, yaml_str: str, model: Type[PydanticBaseModel]) -> Self:
        """Parse from given yaml string, using the given model type to call its parse_obj."""
        return cls._from_dict(_yaml.safe_load(yaml_str), model)

    @classmethod
    def from_yaml(cls, yaml_str: str) -> Self:
        """Parse from given yaml_str."""
        raise NotImplementedError

    @classmethod
    def _from_file(cls, yaml_file: Union[Path, str], model: Type[PydanticBaseModel]) -> Self:
        yaml_file = Path(yaml_file)
        return cls._from_yaml(yaml_file.read_text(encoding="utf-8"), model)

    @classmethod
    def from_file(cls, yaml_file: Union[Path, str]) -> Self:
        """Parse from given yaml_file."""
        raise NotImplementedError


def _set_model_attr(model: PydanticBaseModel, attrs: List[str], value: Any):
    # The `attrs` list represents a path to an attribute in `model`, whose attributes
    # are BaseModels themselves. Therefore we use `getattr` to get a reference to the final
    # BaseModel set to `curr`, then call `setattr` on that BaseModel, using the last attribute
    # name in attrs, and the value passed in.
    curr: PydanticBaseModel = model
    for attr in attrs[:-1]:
        curr = getattr(curr, attr)

    setattr(curr, attrs[-1], value)


def _get_model_attr(model: PydanticBaseModel, attrs: List[str]) -> Any:
    # This is almost the same as _set_model_attr.
    # The `attrs` list represents a path to an attribute in `model`, whose attributes
    # are BaseModels themselves. Therefore we use `getattr` to get a reference to the final
    # BaseModel set to `curr`, then `getattr` on that BaseModel, using the last attribute
    # name in attrs.
    curr: PydanticBaseModel = model
    for attr in attrs[:-1]:
        curr = getattr(curr, attr)

    return getattr(curr, attrs[-1])
