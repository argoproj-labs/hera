from typing import ClassVar, Type

import pytest
from typing_extensions import Annotated

from hera.shared._pydantic import BaseModel
from hera.workflows.resource_base import ModelMapper, ResourceBase


def test_bad_model_mapper():
    class DestModel(BaseModel):
        good: bool

    with pytest.raises(ValueError) as e:

        class BadResource(ResourceBase):
            mapped_model: ClassVar[Type[BaseModel]] = DestModel
            good: Annotated[bool, ModelMapper("good")]
            bar: Annotated[bool, ModelMapper("bad.field")]

    assert "Model key 'bad' does not exist in class test_bad_model_mapper.<locals>.DestModel" == str(e.value)
