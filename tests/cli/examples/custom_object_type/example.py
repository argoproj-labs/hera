from __future__ import annotations

from hera.shared._pydantic import BaseModel
from hera.workflows._mixins import BuildableMixin
from hera.workflows.workflow import Workflow


class ExampleTypeInstance(BaseModel):
    kind: str
    apiVersion: str
    name: str


class ExampleType(BaseModel, BuildableMixin):
    name: str

    def build(self) -> ExampleTypeInstance:
        return ExampleTypeInstance(kind="Example", apiVersion="example.example/v1alpha1", name=self.name)


example_type = ExampleType(name="example")
workflow = Workflow(name=f"{example_type.name}_workflow")
