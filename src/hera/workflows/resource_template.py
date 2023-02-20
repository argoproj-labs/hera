from dataclasses import asdict, dataclass
from typing import List, Optional

from argo_workflows.models import IoArgoprojWorkflowV1alpha1ResourceTemplate


@dataclass
class ResourceTemplate:
    """ResourceTemplate manipulates kubernetes resources.

    Attributes
    ----------
    action: str
        Action to perform to the resource, must be a `kubectl` action.
    failure_condition: Optional[str]
        An expression which describes the conditions of considered
        failed k8s resource step.
    flags: Optional[List[str]]
        Flags is a set of additional options passed to kubectl before
        submitting a resource.
    manifest: Optional[str]
        Kubernetes manifest.
    merge_strategy: Optional[str]
        The strategy used to merge a patch.
    set_owner_reference: Optional[bool]
        When set to True, sets the reference to the workflow on the
        OwnerReference of generated resource. Used for garbage collection
        when workflow is deleted child with owner reference is also deleted.
    success_condition: Optional[str]
        An expression which describes the conditions of the k8s resource
        in which it is acceptable to proceed to the following step.
    """

    action: str
    failure_condition: Optional[str] = None
    flags: Optional[List[str]] = None
    manifest: Optional[str] = None
    merge_strategy: Optional[str] = None
    set_owner_reference: Optional[bool] = None
    success_condition: Optional[str] = None

    def _get_settable_attributes_as_kwargs(self):
        attributes = asdict(self)
        settable_attributes = {k: v for k, v in attributes.items() if v is not None}
        return settable_attributes

    def build(self) -> IoArgoprojWorkflowV1alpha1ResourceTemplate:
        """Builds the resource template specification"""
        settable_attributes = self._get_settable_attributes_as_kwargs()
        return IoArgoprojWorkflowV1alpha1ResourceTemplate(**settable_attributes)
