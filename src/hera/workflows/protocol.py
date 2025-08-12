"""Holds protocol implementations that dictate the functionality associated with Hera objects."""

from typing import Any, List, Optional, Union

from typing_extensions import Protocol, runtime_checkable

from hera.workflows.models import (
    ClusterWorkflowTemplate,
    ContainerSetTemplate,
    CronWorkflow,
    DAGTemplate,
    PersistentVolumeClaim,
    ResourceTemplate,
    ScriptTemplate,
    SuspendTemplate,
    Template,
    Workflow,
    WorkflowTemplate,
)

TTemplate = Union[
    ContainerSetTemplate,
    DAGTemplate,
    ResourceTemplate,
    ScriptTemplate,
    SuspendTemplate,
    Template,
]
"""`TTemplate` is a union type collection of all the model Template classes"""
# Unused in codebase, TBD if deprecated

TWorkflow = Union[
    CronWorkflow,
    ClusterWorkflowTemplate,
    Workflow,
    WorkflowTemplate,
]
"""`TWorkflow` is a union type collection of all the model workflow classes"""


@runtime_checkable
class Templatable(Protocol):
    """This runtime protocol indicates that an object can build its own template representation."""

    name: Optional[str]

    def _build_template(self) -> Template: ...


@runtime_checkable
class VolumeClaimable(Protocol):
    """This runtime protocol indicates that an object can build its own persistent volume claims."""

    def _build_persistent_volume_claims(self) -> Optional[List[PersistentVolumeClaim]]: ...


@runtime_checkable
class Subbable(Protocol):
    """This runtime protocol indicates that an object supports contextualization via the `with` clause."""

    def _add_sub(self, node: Any) -> Any: ...


@runtime_checkable
class Steppable(Protocol):
    """This runtime protocol indicates that an object supports building `Step`/`s` as part of its context."""

    def _build_step(self) -> Any: ...
