from __future__ import annotations

from typing import ClassVar, Type

from typing_extensions import Annotated

from hera.shared._pydantic import BaseModel, Field
from hera.workflows.resource_base import ModelMapper, ResourceBase
from hera.workflows.workflow import Workflow


class ExampleTypeInstance(BaseModel):
    kind: str
    api_version: Annotated[str, Field(alias="apiVersion")]
    name: str


class ExampleType(ResourceBase):
    mapped_model: ClassVar[Type] = ExampleTypeInstance

    name: Annotated[str, ModelMapper("name")]

    def build(self) -> ExampleTypeInstance:
        return ExampleTypeInstance(
            kind="Example",
            api_version="example.example/v1alpha1",
            name=self.name,
        )


example_type = ExampleType(name="example")
workflow = Workflow(name=f"{example_type.name}_workflow")
