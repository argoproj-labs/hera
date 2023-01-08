"""The implementation of a Hera cron workflow for Argo-based cron workflows"""
from typing import Optional

from hera.global_config import GlobalConfig
from hera.models import CreateOptions
from hera.models import WorkflowTemplate as _ModelWorkflowTemplate
from hera.models import (
    WorkflowTemplateCreateRequest,
    WorkflowTemplateDeleteResponse,
    WorkflowTemplateLintRequest,
    WorkflowTemplateUpdateRequest,
)
from hera.workflow import Workflow


class WorkflowTemplate(Workflow):
    """A workflow template representation.

    See `hera.workflow.Workflow` for parameterization.

    Notes
    -----
    See: https://argoproj.github.io/argo-workflows/workflow-templates/
    """

    def build(self) -> _ModelWorkflowTemplate:
        """Builds the workflow"""
        spec = super()._build_spec()
        return _ModelWorkflowTemplate(
            api_version=GlobalConfig.api_version,
            kind=self.__name__,
            metadata=self._build_metadata(),
            spec=spec,
        )

    def create(
        self, namespace: str = GlobalConfig.namespace, create_options: Optional[CreateOptions] = None
    ) -> "WorkflowTemplate":
        """Creates a workflow template"""
        if self.in_context:
            raise ValueError("Cannot invoke `create` when using a Hera context")
        return self.service.create_workflow_template(
            namespace,
            WorkflowTemplateCreateRequest(create_options=create_options, namespace=namespace, template=self.build()),
        )

    def lint(
        self, namespace: str = GlobalConfig.namespace, create_options: Optional[CreateOptions] = None
    ) -> "WorkflowTemplate":
        """Lint the workflow"""
        return self.service.lint_workflow_template(
            namespace,
            WorkflowTemplateLintRequest(
                create_options=create_options,
                namespace=namespace,
                template=self.build(),
            ),
        )

    def update(self, namespace: str = GlobalConfig.namespace) -> "WorkflowTemplate":
        """Updates an existing workflow template"""
        return self.service.update_workflow_template(
            namespace,
            self.name,
            WorkflowTemplateUpdateRequest(
                name=self.name,
                namespace=namespace,
                template=self.build(),
            ),
        )

    def delete(
        self,
        namespace: str = GlobalConfig.namespace,
        grace_period_seconds: Optional[str] = None,
        uid: Optional[str] = None,
        resource_version: Optional[str] = None,
        orphan_dependents: Optional[bool] = None,
        propagation_policy: Optional[str] = None,
        dry_run: Optional[list] = None,
    ) -> WorkflowTemplateDeleteResponse:
        """Deletes the workflow"""
        return self.service.delete_workflow_template(
            namespace,
            self.name,
            grace_period_seconds=grace_period_seconds,
            uid=uid,
            resource_version=resource_version,
            orphan_dependents=orphan_dependents,
            propagation_policy=propagation_policy,
            dry_run=dry_run,
        )


__all__ = ["WorkflowTemplate"]
