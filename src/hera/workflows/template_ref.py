from dataclasses import dataclass

from argo_workflows.models import IoArgoprojWorkflowV1alpha1TemplateRef


@dataclass
class TemplateRef:
    """Reference to a workflow template containing task templates to be shared.

    Parameters
    ----------
    name: str
        The name of the workflow template reference.
    template: str
        The name of the independent task template to reference in the workflow template.
    cluster_scope: bool = False
        Whether the referenced template is cluster scoped or not.
    """

    name: str
    template: str
    cluster_scope: bool = False

    def build(self) -> IoArgoprojWorkflowV1alpha1TemplateRef:
        return IoArgoprojWorkflowV1alpha1TemplateRef(
            name=self.name, template=self.template, cluster_scope=self.cluster_scope
        )
