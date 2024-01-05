from __future__ import annotations

from typing_extensions import Annotated

from hera.shared._pydantic import BaseModel
from hera.workflows.resource_base import ModelMapper, ResourceBase
from hera.workflows.workflow import Workflow


class ExampleTypeInstance(BaseModel):
    kind: str
    apiVersion: str
    name: str


class ExampleType(ResourceBase):
    name: Annotated[str, ModelMapper("name")]

    def build(self) -> ExampleTypeInstance:
        return ExampleTypeInstance(kind="Example", apiVersion="example.example/v1alpha1", name=self.name)


example_type = ExampleType(name="example")
workflow = Workflow(name=f"{example_type.name}_workflow")
