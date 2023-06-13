"""The workflow_template module provides the WorkflowTemplate class

See https://argoproj.github.io/argo-workflows/workflow-templates/
for more on WorkflowTemplates.
"""
from typing import Type, Union

try:
    from typing import Annotated, get_type_hints
except ImportError:
    from typing_extensions import Annotated, get_type_hints
from pathlib import Path

from pydantic import validator

from hera.exceptions import NotFound
from hera.workflows.models import (
    ObjectMeta,
    WorkflowSpec as _ModelWorkflowSpec,
    WorkflowTemplate as _ModelWorkflowTemplate,
    WorkflowTemplateCreateRequest,
    WorkflowTemplateLintRequest,
    WorkflowTemplateUpdateRequest,
)
from hera.workflows.protocol import TWorkflow
from hera.workflows.workflow import Workflow


class WorkflowTemplate(Workflow):
    """WorkflowTemplates are definitions of Workflows that live in your cluster. This allows you
    to create a library of frequently-used templates and reuse them by referencing them from your
    Workflows.
    """

    class _WorkflowTemplateModelMapper(Workflow._WorkflowModelMapper):
        @classmethod
        def _get_model_class(cls) -> Type[_ModelWorkflowTemplate]:
            return _ModelWorkflowTemplate

    # Removes status mapping
    status: Annotated[get_type_hints(Workflow)["status"], _WorkflowTemplateModelMapper("")] = None

    # WorkflowTemplate fields match Workflow exactly except for `status`, which WorkflowTemplate
    # does not have - https://argoproj.github.io/argo-workflows/fields/#workflowtemplate
    @validator("status", pre=True, always=True)
    def _set_status(cls, v):
        if v is not None:
            raise ValueError("status is not a valid field on a WorkflowTemplate")

    def create(self) -> TWorkflow:  # type: ignore
        """Creates the WorkflowTemplate on the Argo cluster."""
        assert self.workflows_service, "workflow service not initialized"
        assert self.namespace, "workflow namespace not defined"
        return self.workflows_service.create_workflow_template(
            WorkflowTemplateCreateRequest(template=self.build()), namespace=self.namespace
        )

    def get(self) -> TWorkflow:
        """Attempts to get a workflow template based on the parameters of this template e.g. name + namespace"""
        assert self.workflows_service, "workflow service not initialized"
        assert self.namespace, "workflow namespace not defined"
        assert self.name, "workflow name not defined"
        return self.workflows_service.get_workflow_template(name=self.name, namespace=self.namespace)

    def update(self) -> TWorkflow:
        """
        Attempts to perform a workflow template update based on the parameters of this template
        e.g. name, namespace. Note that this creates the template if it does not exist. In addition, this performs
        a get prior to updating to get the resource version to update in the first place. If you know the template
        does not exist ahead of time, it is more efficient to use `create()` directly to avoid one round trip.
        """
        assert self.workflows_service, "workflow service not initialized"
        assert self.namespace, "workflow namespace not defined"
        assert self.name, "workflow name not defined"
        # we always need to do a get prior to updating to get the resource version to update in the first place
        # https://github.com/argoproj/argo-workflows/pull/5465#discussion_r597797052

        template = self.build()
        try:
            curr = self.get()
            template.metadata.resource_version = curr.metadata.resource_version
        except NotFound:
            return self.create()
        return self.workflows_service.update_workflow_template(
            self.name,
            WorkflowTemplateUpdateRequest(template=template),
            namespace=self.namespace,
        )

    def lint(self) -> TWorkflow:
        """Lints the WorkflowTemplate using the Argo cluster."""
        assert self.workflows_service, "workflow service not initialized"
        assert self.namespace, "workflow namespace not defined"
        return self.workflows_service.lint_workflow_template(
            WorkflowTemplateLintRequest(template=self.build()), namespace=self.namespace
        )

    def build(self) -> TWorkflow:
        """Builds the WorkflowTemplate and its components into an Argo schema WorkflowTemplate object."""
        self = self._dispatch_hooks()

        model_workflow = _ModelWorkflowTemplate(
            metadata=ObjectMeta(),
            spec=_ModelWorkflowSpec(),
        )

        return WorkflowTemplate._WorkflowTemplateModelMapper.build_model(self, model_workflow)

    @classmethod
    def from_yaml(cls: "WorkflowTemplate", yaml_file: Union[Path, str]) -> "WorkflowTemplate":
        """Create a WorkflowTemplate from a WorkflowTemplate contained in a YAML file.

        Usage:
            my_workflow = WorkflowTemplate.from_yaml(yaml_file)
        """
        return cls._from_yaml(yaml_file, _ModelWorkflowTemplate)


__all__ = ["WorkflowTemplate"]
