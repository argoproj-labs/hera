from typing import List, Optional

from argo_workflows.model.capabilities import Capabilities
from argo_workflows.model.pod_security_context import PodSecurityContext
from argo_workflows.model.security_context import SecurityContext

from pydantic import BaseModel


class WorkflowSecurityContext(BaseModel):
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

    run_as_user: Optional[int] = None
    run_as_group: Optional[int] = None
    fs_group: Optional[int] = None
    run_as_non_root: Optional[bool] = None

    def get_security_context(self) -> PodSecurityContext:
        return PodSecurityContext(
            run_as_user=self.run_as_user,
            run_as_group=self.run_as_group,
            fs_group=self.fs_group,
            run_as_non_root=self.run_as_non_root,
        )


class TaskSecurityContext(BaseModel):
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

    run_as_user: Optional[int] = None
    run_as_group: Optional[int] = None
    run_as_non_root: Optional[bool] = None
    additional_capabilities: List[str] = None

    def _get_capabilties(self):
        if self.additional_capabilities:
            return Capabilities(add=self.additional_capabilities)

    def get_security_context(self) -> SecurityContext:
        capabilities = self._get_capabilties()
        security_context = SecurityContext(
            run_as_user=self.run_as_user,
            run_as_group=self.run_as_group,
            run_as_non_root=self.run_as_non_root,
            capabilities=capabilities,
        )
        if capabilities:
            setattr(security_context, 'capabilities', capabilities)
        return security_context