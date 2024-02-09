from typing import ClassVar, Type

import pytest
from typing_extensions import Annotated

from hera.shared._pydantic import BaseModel, Field, PydanticBaseModel
from hera.workflows.resource_base import ModelMapper, ResourceBase


def test_bad_model_mapper():
    class DestModel(BaseModel):
        api_version: str
        kind: str
        good: bool

    with pytest.raises(ValueError) as e:

        class BadResource(ResourceBase):
            mapped_model: ClassVar[Type[PydanticBaseModel]] = DestModel
            good: Annotated[bool, ModelMapper("good")]
            bar: Annotated[bool, ModelMapper("bad.field")]

    assert "Model key 'bad' does not exist in class test_bad_model_mapper.<locals>.DestModel" == str(e.value)


def test_missing_mapped_model():
    with pytest.raises(AttributeError) as e:

        class BadResource(ResourceBase):
            good: Annotated[bool, ModelMapper("good")]
            bar: Annotated[bool, ModelMapper("bad.field")]

    assert (
        "test_missing_mapped_model.<locals>.BadResource must define a `mapped_model` attribute, which specifies the Pydantic model to which this resource's attributes map."
        == str(e.value)
    )


def test_valid_resource_base():
    class DestModel(BaseModel):
        api_version: Annotated[str, Field(alias="apiVersion")] = "v1alpha1"
        kind: str = ""
        good: bool = False

    class GoodResource(ResourceBase):
        mapped_model: ClassVar[Type[PydanticBaseModel]] = DestModel

        good: Annotated[bool, ModelMapper("good")]

    resource = GoodResource(good=True)
    result = resource.to_dict()
    assert result == {
        "apiVersion": "v1alpha1",
        "kind": "GoodResource",
        "good": True,
    }
