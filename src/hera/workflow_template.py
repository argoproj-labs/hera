"""The implementation of a Hera cron workflow for Argo-based cron workflows"""
from typing import Tuple

from argo_workflows.models import IoArgoprojWorkflowV1alpha1WorkflowTemplate

from hera.workflow import Workflow


class WorkflowTemplate(Workflow):
    """A workflow template representation.

    See `hera.workflow.Workflow` for parameterization.

    See Also
    --------
    https://argoproj.github.io/argo-workflows/workflow-templates/
    """

    def build(self) -> IoArgoprojWorkflowV1alpha1WorkflowTemplate:
        """Builds the workflow"""
        spec = super()._build_spec(workflow_template=True)
        return IoArgoprojWorkflowV1alpha1WorkflowTemplate(metadata=self._build_metadata(), spec=spec)

    def create(self) -> IoArgoprojWorkflowV1alpha1WorkflowTemplate:
        """Creates a workflow template"""
        if self.in_context:
            raise ValueError("Cannot invoke `create` when using a Hera context")
        assert self.dag is not None
        return self.service.create_workflow_template(self.build())

    def update(self) -> Tuple[object, int, dict]:
        """Updates an existing workflow template"""
        return self.service.update_workflow_template(self.name, self.build())

    def delete(self) -> Tuple[object, int, dict]:
        """Deletes the workflow"""
        return self.service.delete_workflow_template(self.name)
