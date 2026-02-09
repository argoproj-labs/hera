"""Module that provides Hera objects for cluster workflow templates."""

from dataclasses import dataclass

from hera.exceptions import NotFound
from hera.workflows.async_service import AsyncWorkflowsService
from hera.workflows.models import (
    ClusterWorkflowTemplate as _ModelClusterWorkflowTemplate,
    ClusterWorkflowTemplateCreateRequest,
    ClusterWorkflowTemplateLintRequest,
    ClusterWorkflowTemplateUpdateRequest,
)
from hera.workflows.protocol import TWorkflow
from hera.workflows.service import WorkflowsService
from hera.workflows.workflow_template import WorkflowTemplate


@dataclass(kw_only=True)
class ClusterWorkflowTemplate(WorkflowTemplate):
    """ClusterWorkflowTemplates are cluster scoped templates.

    Since cluster workflow templates are scoped at the cluster level, they are available globally in the cluster.
    """

    def __post_init__(self):
        """Set class defaults via __post_init__, then ensure namespace is not set."""
        super().__post_init__()

        if self.namespace is not None:
            raise ValueError("namespace is not a valid field on a ClusterWorkflowTemplate")

    def create(self) -> TWorkflow:  # type: ignore
        """Creates the ClusterWorkflowTemplate on the Argo cluster."""
        assert isinstance(self.workflows_service, WorkflowsService), "workflows service not initialized"
        return self.workflows_service.create_cluster_workflow_template(
            ClusterWorkflowTemplateCreateRequest(template=self.build())  # type: ignore
        )

    def get(self) -> TWorkflow:
        """Attempts to get a workflow template based on the parameters of this template e.g. name + namespace."""
        assert isinstance(self.workflows_service, WorkflowsService), "workflows service not initialized"
        assert self.name, "workflow name not defined"
        return self.workflows_service.get_cluster_workflow_template(name=self.name)

    def update(self) -> TWorkflow:
        """Attempts to perform a workflow template update based on the parameters of this template.

        Note that this creates the template if it does not exist. In addition, this performs
        a get prior to updating to get the resource version to update in the first place. If you know the template
        does not exist ahead of time, it is more efficient to use `create()` directly to avoid one round trip.
        """
        assert isinstance(self.workflows_service, WorkflowsService), "workflows service not initialized"
        assert self.name, "workflow name not defined"
        # we always need to do a get prior to updating to get the resource version to update in the first place
        # https://github.com/argoproj/argo-workflows/pull/5465#discussion_r597797052

        template = self.build()
        try:
            curr = self.get()
            template.metadata.resource_version = curr.metadata.resource_version
        except NotFound:
            return self.create()
        return self.workflows_service.update_cluster_workflow_template(
            self.name,
            ClusterWorkflowTemplateUpdateRequest(template=template),  # type: ignore
        )

    def lint(self) -> TWorkflow:
        """Lints the ClusterWorkflowTemplate using the Argo cluster."""
        assert isinstance(self.workflows_service, WorkflowsService), "workflows service not initialized"
        return self.workflows_service.lint_cluster_workflow_template(
            ClusterWorkflowTemplateLintRequest(template=self.build())  # type: ignore
        )

    async def async_create(self) -> TWorkflow:  # type: ignore
        """Creates the ClusterWorkflowTemplate on the Argo cluster."""
        assert isinstance(self.workflows_service, AsyncWorkflowsService), "workflows service not initialized"
        return await self.workflows_service.create_cluster_workflow_template(
            ClusterWorkflowTemplateCreateRequest(template=self.build())  # type: ignore
        )

    async def async_get(self) -> TWorkflow:
        """Attempts to get a workflow template based on the parameters of this template e.g. name + namespace."""
        assert isinstance(self.workflows_service, AsyncWorkflowsService), "workflows service not initialized"
        assert self.name, "workflow name not defined"
        return await self.workflows_service.get_cluster_workflow_template(name=self.name)

    async def async_update(self) -> TWorkflow:
        """Attempts to perform a workflow template update based on the parameters of this template.

        Note that this creates the template if it does not exist. In addition, this performs
        a get prior to updating to get the resource version to update in the first place. If you know the template
        does not exist ahead of time, it is more efficient to use `create()` directly to avoid one round trip.
        """
        assert isinstance(self.workflows_service, AsyncWorkflowsService), "workflows service not initialized"
        assert self.name, "workflow name not defined"
        # we always need to do a get prior to updating to get the resource version to update in the first place
        # https://github.com/argoproj/argo-workflows/pull/5465#discussion_r597797052

        template = self.build()
        try:
            curr = await self.async_get()
            template.metadata.resource_version = curr.metadata.resource_version
        except NotFound:
            return await self.async_create()
        return await self.workflows_service.update_cluster_workflow_template(
            self.name,
            ClusterWorkflowTemplateUpdateRequest(template=template),  # type: ignore
        )

    async def async_lint(self) -> TWorkflow:
        """Lints the ClusterWorkflowTemplate using the Argo cluster."""
        assert isinstance(self.workflows_service, AsyncWorkflowsService), "workflows service not initialized"
        return await self.workflows_service.lint_cluster_workflow_template(
            ClusterWorkflowTemplateLintRequest(template=self.build())  # type: ignore
        )

    def build(self) -> TWorkflow:
        """Builds the ClusterWorkflowTemplate and its components into an Argo schema ClusterWorkflowTemplate object."""
        # Note that ClusterWorkflowTemplates are exactly the same as WorkflowTemplates except for the kind which is
        # handled in Workflow._set_kind (by __name__). When using ClusterWorkflowTemplates via templateRef, clients
        # should specify cluster_scope=True, but that is an intrinsic property of ClusterWorkflowTemplates from our
        # perspective.
        return _ModelClusterWorkflowTemplate(**super().build().model_dump())


__all__ = ["ClusterWorkflowTemplate"]
