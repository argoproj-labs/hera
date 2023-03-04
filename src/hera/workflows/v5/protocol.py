from typing import Any, Protocol, Union, runtime_checkable

from hera.workflows.models import (
    ContainerSetTemplate,
    DAGTemplate,
    ResourceTemplate,
    ScriptTemplate,
    SuspendTemplate,
    Template,
)

TTemplate = Union[
    ContainerSetTemplate,
    DAGTemplate,
    ResourceTemplate,
    ScriptTemplate,
    SuspendTemplate,
    Template,
]


@runtime_checkable
class Templatable(Protocol):
    def _build_template(self) -> TTemplate:
        ...


@runtime_checkable
class Subbable(Protocol):
    def _add_sub(self, node: Any) -> Template:
        ...
