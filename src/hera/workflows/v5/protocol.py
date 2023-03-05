from typing import Any, Dict, List, Optional, Union

from typing_extensions import Protocol, runtime_checkable

from hera.workflows.models import (
    ContainerSetTemplate,
    ContinueOn,
    DAGTemplate,
    Item,
    LifecycleHook,
    ResourceTemplate,
    ScriptTemplate,
    Sequence,
    SuspendTemplate,
    Template,
    TemplateRef,
)
from hera.workflows.v5._mixins import _DAGTaskMixin

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


@runtime_checkable
class Callable(Protocol):
    def __call__(
        self,
        continue_on: Optional[ContinueOn] = None,
        dependencies: Optional[List[str]] = None,
        depends: Optional[str] = None,
        hooks: Optional[Dict[str, LifecycleHook]] = None,
        on_exit: Optional[str] = None,
        template: Optional[str] = None,
        template_ref: Optional[TemplateRef] = None,
        when: Optional[str] = None,
        with_items: Optional[List[Item]] = None,
        with_param: Optional[str] = None,
        with_sequence: Optional[Sequence] = None,
    ) -> _DAGTaskMixin:
        ...
