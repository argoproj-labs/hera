from dataclasses import asdict, dataclass, field
from typing import List, Optional

from argo_workflows.model_utils import ModelNormal
from argo_workflows.models import Capabilities, PodSecurityContext, SecurityContext


@dataclass
class BaseSecurityContext:
    """Abstract class to accommodate the shared functionality of task and workflow context.

    Attributes
    ----------
    privileged: Optional[bool] = None
        Allow all the task's container to run as privileged
    run_as_user: Optional[int]
        Sets the user id of the user running in all the containers in the workflow.
    run_as_group: Optional[int]
        Sets the user id of the user running in all the containers in the workflow.
    run_as_non_root: Optional[bool]
        Validates that all the tasks' container does not run as root, i.e UID does not equal 0.
    """

    privileged: Optional[bool] = None
    run_as_user: Optional[int] = None
    run_as_group: Optional[int] = None
    run_as_non_root: Optional[bool] = None

    def _get_settable_attributes_as_kwargs(self) -> dict:
        """Assembles non-None attribute mappings, from key to value"""
        attributes = asdict(self)
        settable_attributes = {k: v for k, v in attributes.items() if v is not None}
        return settable_attributes

    def build(self) -> ModelNormal:
        raise NotImplementedError()


@dataclass
class WorkflowSecurityContext(BaseSecurityContext):
    """Defines workflow level security attributes and settings.

    Attributes
    ----------
    privileged: Optional[bool] = None
        Allow all the task's container to run as privileged
    run_as_user: Optional[int]
        Sets the user id of the user running in all the containers in the workflow.
    run_as_group: Optional[int]
        Sets the user id of the user running in all the containers in the workflow.
    fs_group: Optional[int]
        Allow an additional group to all the users running on the containers in the workflow.
    run_as_non_root: Optional[bool]
        Validates that all the tasks' container does not run as root, i.e, UID does not equal 0.
    """

    fs_group: Optional[int] = None

    def get_security_context(self) -> PodSecurityContext:
        """Assembles the security context of the workflow"""
        settable_attributes = self._get_settable_attributes_as_kwargs()
        security_context = PodSecurityContext(**settable_attributes)
        return security_context

    def build(self) -> PodSecurityContext:
        """Wrapper around legacy `get_security_context`"""
        return self.get_security_context()


@dataclass
class TaskSecurityContext(BaseSecurityContext):
    """Defines task level security attributes and settings overrides the WorkflowSecurityContext settings.

    Attributes
    ----------
    privileged: Optional[bool] = None
        Allow all the task's container to run as privileged
    run_as_user: Optional[int]
        Sets the user id of the user running in the task's container.
    run_as_group: Optional[int]
        Sets the group id of the user running in the task's container.
    run_as_non_root: Optional[bool]
        Validates that the tasks container does not run as root, i.e UID does not equal 0.
    additional_capabilities: List[str]
        List of POSIX capabilities to add to the task's container.
    """

    additional_capabilities: List[str] = field(default_factory=list)

    def _get_capabilties(self) -> Capabilities:
        """Assembles the capabilities of the task security context"""
        if self.additional_capabilities:
            return Capabilities(add=self.additional_capabilities)

    def _get_settable_attributes_as_kwargs(self) -> dict:
        settable_attributes = super()._get_settable_attributes_as_kwargs()
        if settable_attributes.pop("additional_capabilities", None):
            settable_attributes["capabilities"] = self._get_capabilties()
        return settable_attributes

    def build(self) -> SecurityContext:
        """Assembles the security context of the pod"""
        settable_attributes = self._get_settable_attributes_as_kwargs()
        security_context = SecurityContext(**settable_attributes)
        return security_context
