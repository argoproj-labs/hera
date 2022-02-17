from typing import List, Optional

from argo_workflows.model.capabilities import Capabilities
from argo_workflows.model.pod_security_context import PodSecurityContext
from argo_workflows.model.security_context import SecurityContext
from pydantic import BaseModel


class BaseSecurityContext(BaseModel):
    """Abstract class to accomedate the shared functionallity of task and workflow context."""

    run_as_user: Optional[int] = None
    run_as_group: Optional[int] = None
    run_as_non_root: Optional[bool] = None

    def _get_settable_attributes_as_kwargs(self):
        attributes = dict(self)
        settable_attributes = {k: v for k, v in attributes.items() if v is not None}
        return settable_attributes


class WorkflowSecurityContext(BaseSecurityContext):
    """Defines workflow level sercurity attributes and settings.

    Attributes
    ----------
    run_as_user: Optinal[int]
        Sets the user id of the user running in all of the containers in the workflow.
    run_as_group: Optinal[int]
        Sets the user id of the user running in all of the containers in the workflow.
    fs_group: Optional[int]
        Allow to add an additional group to the all users running on allof the containers in the workflow.
    run_as_non_root: Optional[bool]
        Validates that all the tasks container does not run as root, i.e UID does not equal 0.
    """

    fs_group: Optional[int] = None

    def get_security_context(self) -> PodSecurityContext:
        settable_attributes = self._get_settable_attributes_as_kwargs()
        security_context = PodSecurityContext(**settable_attributes)
        return security_context


class TaskSecurityContext(BaseSecurityContext):
    """Defines task level sercurity attributes and settings,
    overrides the WorkflowSecurityContext settings.

    Attributes
    ----------
    run_as_user: Optinal[int]
        Sets the user id of the user running in the task's container.
    run_as_group: Optinal[int]
        Sets the group id of the user running in the task's container.
    run_as_non_root: Optional[bool]
        Validates that the tasks container does not run as root, i.e UID does not equal 0.
    additional_capabilities: List[str]
        List of POSIX capabilities to add to the task's container.
    """

    additional_capabilities: List[str] = None

    def _get_capabilties(self):
        if self.additional_capabilities:
            return Capabilities(add=self.additional_capabilities)

    def _get_settable_attributes_as_kwargs(self):
        settable_attributes = super()._get_settable_attributes_as_kwargs()
        if settable_attributes.pop("additional_capabilities", None):
            settable_attributes["capabilities"] = self._get_capabilties()
        return settable_attributes

    def get_security_context(self) -> SecurityContext:
        settable_attributes = self._get_settable_attributes_as_kwargs()
        security_context = SecurityContext(**settable_attributes)
        return security_context
