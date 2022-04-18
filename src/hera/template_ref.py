from argo_workflows.models import IoArgoprojWorkflowV1alpha1TemplateRef
from pydantic import BaseModel


class TemplateRef(BaseModel):
    """Reference to a workflow template containing task templates to be shared.

    Parameters
    ----------
    name: str
        The name of the workflow template reference.
    template: str
        The name of the independent task template to reference in the workflow template.
    """

    name: str
    template: str

    @property
    def argo_spec(self) -> IoArgoprojWorkflowV1alpha1TemplateRef:
        return IoArgoprojWorkflowV1alpha1TemplateRef(name=self.name, template=self.template)
