from hera.workflows.models import (
    WorkflowTemplate as _ModelWorkflowTemplate,
    WorkflowTemplateCreateRequest,
    WorkflowTemplateLintRequest,
)
from hera.workflows.workflow import Workflow


class WorkflowTemplate(Workflow):
    def create(self) -> _ModelWorkflowTemplate:
        assert self.workflows_service, "workflow service not initialized"
        assert self.namespace, "workflow namespace not defined"
        return self.workflows_service.create_workflow_template(
            self.namespace, WorkflowTemplateCreateRequest(workflow=self.build())
        )

    def lint(self) -> _ModelWorkflowTemplate:
        assert self.workflows_service, "workflow service not initialized"
        assert self.namespace, "workflow namespace not defined"
        return self.workflows_service.lint_workflow_template(
            self.namespace, WorkflowTemplateLintRequest(workflow=self.build())
        )


__all__ = ["WorkflowTemplate"]
