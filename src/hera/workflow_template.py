"""The implementation of a Hera cron workflow for Argo-based cron workflows"""
from typing import cast

from hera.global_config import GlobalConfig
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

    def build(self: "WorkflowTemplate") -> _ModelWorkflowTemplate:  # type: ignore
        """Builds the workflow"""
        spec = super()._build_spec()
        return _ModelWorkflowTemplate(
            api_version=GlobalConfig.api_version,
            kind=self.__class__.__name__,
            metadata=self._build_metadata(),
            spec=spec,
        )

    @staticmethod
    def from_model(m: _ModelWorkflowTemplate) -> "WorkflowTemplate":  # type: ignore
        return WorkflowTemplate(api_version=m.api_version, **m.metadata.dict(), **m.spec.dict())

    def create(
        self: "WorkflowTemplate",
        namespace: str = GlobalConfig.namespace,
        **create_kwargs,
    ) -> "WorkflowTemplate":
        """Creates a workflow template"""
        if self.in_context:
            raise ValueError("Cannot invoke `create` when using a Hera context")
        return WorkflowTemplate.from_model(
            self.service.create_workflow_template(
                namespace,
                WorkflowTemplateCreateRequest(namespace=namespace, template=self.build(), **create_kwargs),
            )
        )

    def lint(
        self: "WorkflowTemplate",
        namespace: str = GlobalConfig.namespace,
        **create_kwargs,
    ) -> "WorkflowTemplate":
        """Lint the workflow"""
        return WorkflowTemplate.from_model(
            self.service.lint_workflow_template(
                namespace,
                WorkflowTemplateLintRequest(
                    namespace=namespace,
                    template=self.build(),
                    **create_kwargs,
                ),
            )
        )

    def update(self: "WorkflowTemplate", namespace: str = GlobalConfig.namespace) -> "WorkflowTemplate":
        """Updates an existing workflow template"""
        return WorkflowTemplate.from_model(
            self.service.update_workflow_template(
                namespace,
                cast(str, self.name),
                WorkflowTemplateUpdateRequest(
                    name=self.name,
                    namespace=namespace,
                    template=self.build(),
                ),
            )
        )

    def delete(  # type: ignore
        self: "WorkflowTemplate", namespace: str = GlobalConfig.namespace, **delete_kwargs
    ) -> WorkflowTemplateDeleteResponse:  # type: ignore
        """Deletes the workflow"""
        assert self.name is not None, "Cannot delete a workflow template without a `name` set"
        return self.service.delete_workflow_template(namespace, cast(str, self.name), **delete_kwargs)


__all__ = ["WorkflowTemplate"]
