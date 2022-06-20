from typing import List, Optional

from argo_workflows.models import IoArgoprojWorkflowV1alpha1ResourceTemplate
from pydantic import BaseModel


class ResourceTemplate(BaseModel):

    action: str
    failure_condition: Optional[str] = None
    flags: Optional[List[str]] = None
    manifest: Optional[str] = None
    merge_strategy: Optional[str] = None
    set_owner_reference: Optional[bool] = None
    success_condition: Optional[str] = None

    def _get_settable_attributes_as_kwargs(self):
        attributes = dict(self)
        settable_attributes = {k: v for k, v in attributes.items() if v is not None}
        return settable_attributes

    def get_resource_template(self) -> IoArgoprojWorkflowV1alpha1ResourceTemplate:
        settable_attributes = self._get_settable_attributes_as_kwargs()
        return IoArgoprojWorkflowV1alpha1ResourceTemplate(**settable_attributes)
