"""The implementation of a Hera cron workflow for Argo-based cron workflows"""
from typing import Tuple

from argo_workflows.models import IoArgoprojWorkflowV1alpha1WorkflowTemplate

from hera.host_config import get_global_api_version
from hera.workflow import Workflow


class WorkflowTemplate(Workflow):
    """A workflow template representation.

    See `hera.workflow.Workflow` for parameterization.

    Notes
    -----
    See: https://argoproj.github.io/argo-workflows/workflow-templates/
    """

    def build(self) -> IoArgoprojWorkflowV1alpha1WorkflowTemplate:
        """Builds the workflow"""
        spec = super()._build_spec()
        return IoArgoprojWorkflowV1alpha1WorkflowTemplate(
            api_version=get_global_api_version(),
            kind=self.__class__.__name__,
            metadata=self._build_metadata(),
            spec=spec,
        )

    def create(self) -> "WorkflowTemplate":
        """Creates a workflow template"""
        if self.in_context:
            raise ValueError("Cannot invoke `create` when using a Hera context")
        self.service.create_workflow_template(self.build())
        return self

    def lint(self) -> "WorkflowTemplate":
        """Lint the workflow"""
        self.service.lint_workflow_template(self.build())
        return self

    def update(self) -> "WorkflowTemplate":
        """Updates an existing workflow template"""
        self.service.update_workflow_template(self.name, self.build())
        return self

    def delete(self) -> Tuple[object, int, dict]:
        """Deletes the workflow"""
        return self.service.delete_workflow_template(self.name)
