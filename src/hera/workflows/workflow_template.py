"""The workflow_template module provides the WorkflowTemplate class.

See https://argoproj.github.io/argo-workflows/workflow-templates/
for more on WorkflowTemplates.
"""

from pathlib import Path
from typing import Annotated, Dict, Optional, Type, Union, cast

from hera.exceptions import NotFound
from hera.shared._pydantic import BaseModel, validator
from hera.workflows._meta_mixins import ModelMapperMixin
from hera.workflows.async_service import AsyncWorkflowsService
from hera.workflows.models import (
    ObjectMeta,
    WorkflowSpec as _ModelWorkflowSpec,
    WorkflowStatus as _ModelWorkflowStatus,
    WorkflowTemplate as _ModelWorkflowTemplate,
    WorkflowTemplateCreateRequest,
    WorkflowTemplateLintRequest,
    WorkflowTemplateUpdateRequest,
)
from hera.workflows.protocol import TWorkflow
from hera.workflows.service import WorkflowsService
from hera.workflows.workflow import NAME_LIMIT, Workflow, _WorkflowModelMapper

# The length of the random suffix used for generate_name
# length (5) from https://github.com/kubernetes/kubernetes/blob/6195f96e/staging/src/k8s.io/apiserver/pkg/storage/names/generate.go#L45
_SUFFIX_LEN = 5

# The max name length comes from https://github.com/kubernetes/kubernetes/blob/6195f96e/staging/src/k8s.io/apiserver/pkg/storage/names/generate.go#L44
# We want to truncate according to SUFFIX_LEN
_TRUNCATE_LENGTH = NAME_LIMIT - _SUFFIX_LEN


class _WorkflowTemplateModelMapper(_WorkflowModelMapper):
    @classmethod
    def _get_model_class(cls) -> Type[BaseModel]:
        return _ModelWorkflowTemplate  # type: ignore


class WorkflowTemplate(Workflow):
    """WorkflowTemplates are definitions of Workflows that live in your namespace in your cluster.

    This allows you to create a library of frequently-used templates and reuse them by referencing
    them from your Workflows.
    """

    # Removes status mapping
    status: Annotated[Optional[_ModelWorkflowStatus], _WorkflowTemplateModelMapper("")] = None

    # WorkflowTemplate fields match Workflow exactly except for `status`, which WorkflowTemplate
    # does not have - https://argoproj.github.io/argo-workflows/fields/#workflowtemplate
    @validator("status", pre=True, always=True)
    def _set_status(cls, v):
        if v is not None:
            raise ValueError("status is not a valid field on a WorkflowTemplate")

    def create(self) -> TWorkflow:  # type: ignore
        """Creates the WorkflowTemplate on the Argo cluster."""
        assert isinstance(self.workflows_service, WorkflowsService), "workflows service not initialized"
        assert self.namespace, "workflow namespace not defined"
        return self.workflows_service.create_workflow_template(
            WorkflowTemplateCreateRequest(template=self.build()),  # type: ignore
            namespace=self.namespace,
        )

    def get(self) -> TWorkflow:
        """Attempts to get a workflow template based on the parameters of this template e.g. name + namespace."""
        assert isinstance(self.workflows_service, WorkflowsService), "workflows service not initialized"
        assert self.namespace, "workflow namespace not defined"
        assert self.name, "workflow name not defined"
        return self.workflows_service.get_workflow_template(name=self.name, namespace=self.namespace)

    def update(self) -> TWorkflow:
        """Attempts to perform a template update based on the parameters of this template.

        This creates the template if it does not exist. In addition, this performs
        a get prior to updating to get the resource version to update in the first place. If you know the template
        does not exist ahead of time, it is more efficient to use `create()` directly to avoid one round trip.
        """
        assert isinstance(self.workflows_service, WorkflowsService), "workflows service not initialized"
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
            WorkflowTemplateUpdateRequest(template=template),  # type: ignore
            namespace=self.namespace,
        )

    def lint(self) -> TWorkflow:
        """Lints the WorkflowTemplate using the Argo cluster."""
        assert isinstance(self.workflows_service, WorkflowsService), "workflows service not initialized"
        assert self.namespace, "workflow namespace not defined"
        return self.workflows_service.lint_workflow_template(
            WorkflowTemplateLintRequest(template=self.build()),  # type: ignore
            namespace=self.namespace,
        )

    async def async_create(self) -> TWorkflow:  # type: ignore
        """Creates the WorkflowTemplate on the Argo cluster."""
        assert isinstance(self.workflows_service, AsyncWorkflowsService), "workflows service not initialized"
        assert self.namespace, "workflow namespace not defined"
        return await self.workflows_service.create_workflow_template(
            WorkflowTemplateCreateRequest(template=self.build()),  # type: ignore
            namespace=self.namespace,
        )

    async def async_get(self) -> TWorkflow:
        """Attempts to get a workflow template based on the parameters of this template e.g. name + namespace."""
        assert isinstance(self.workflows_service, AsyncWorkflowsService), "workflows service not initialized"
        assert self.namespace, "workflow namespace not defined"
        assert self.name, "workflow name not defined"
        return await self.workflows_service.get_workflow_template(name=self.name, namespace=self.namespace)

    async def async_update(self) -> TWorkflow:
        """Attempts to perform a template update based on the parameters of this template.

        This creates the template if it does not exist. In addition, this performs
        a get prior to updating to get the resource version to update in the first place. If you know the template
        does not exist ahead of time, it is more efficient to use `create()` directly to avoid one round trip.
        """
        assert isinstance(self.workflows_service, AsyncWorkflowsService), "workflows service not initialized"
        assert self.namespace, "workflow namespace not defined"
        assert self.name, "workflow name not defined"
        # we always need to do a get prior to updating to get the resource version to update in the first place
        # https://github.com/argoproj/argo-workflows/pull/5465#discussion_r597797052

        template = self.build()
        try:
            curr = await self.async_get()
            template.metadata.resource_version = curr.metadata.resource_version
        except NotFound:
            return await self.async_create()
        return await self.workflows_service.update_workflow_template(
            self.name,
            WorkflowTemplateUpdateRequest(template=template),  # type: ignore
            namespace=self.namespace,
        )

    async def async_lint(self) -> TWorkflow:
        """Lints the WorkflowTemplate using the Argo cluster."""
        assert isinstance(self.workflows_service, AsyncWorkflowsService), "workflows service not initialized"
        assert self.namespace, "workflow namespace not defined"
        return await self.workflows_service.lint_workflow_template(
            WorkflowTemplateLintRequest(template=self.build()),  # type: ignore
            namespace=self.namespace,
        )

    def build(self) -> TWorkflow:
        """Builds the WorkflowTemplate and its components into an Argo schema WorkflowTemplate object."""
        self = self._dispatch_hooks()

        model_workflow = _ModelWorkflowTemplate(
            metadata=ObjectMeta(),
            spec=_ModelWorkflowSpec(),
        )

        return _WorkflowTemplateModelMapper.build_model(WorkflowTemplate, self, model_workflow)

    @classmethod
    def from_dict(cls, model_dict: Dict) -> ModelMapperMixin:
        """Create a WorkflowTemplate from a WorkflowTemplate contained in a dict.

        Examples:
            >>> my_workflow_template = WorkflowTemplate(name="my-wft")
            >>> my_workflow_template == WorkflowTemplate.from_dict(my_workflow_template.to_dict())
            True
        """
        return cls._from_dict(model_dict, _ModelWorkflowTemplate)

    @classmethod
    def from_yaml(cls, yaml_str: str) -> ModelMapperMixin:
        """Create a WorkflowTemplate from a WorkflowTemplate contained in a YAML string.

        Examples:
            >>> my_workflow_template = WorkflowTemplate.from_yaml(yaml_str)
        """
        return cls._from_yaml(yaml_str, _ModelWorkflowTemplate)

    @classmethod
    def from_file(cls, yaml_file: Union[Path, str]) -> ModelMapperMixin:
        """Create a WorkflowTemplate from a WorkflowTemplate contained in a YAML file.

        Examples:
            >>> yaml_file = Path(...)
            >>> my_workflow_template = WorkflowTemplate.from_file(yaml_file)
        """
        return cls._from_file(yaml_file, _ModelWorkflowTemplate)

    def _get_as_workflow(self, generate_name: Optional[str]) -> Workflow:
        workflow = cast(Workflow, Workflow.from_dict(self.to_dict()))
        workflow.kind = "Workflow"
        workflow.workflows_service = self.workflows_service  # bind this workflow to the same service

        if generate_name is not None:
            workflow.generate_name = generate_name
        else:
            # As this function is mainly for improved DevEx when iterating on a WorkflowTemplate, we do a basic
            # truncation of the WT's name in case it being > _TRUNCATE_LENGTH, to assign to generate_name.
            assert workflow.name is not None
            workflow.generate_name = workflow.name[:_TRUNCATE_LENGTH]

        workflow.name = None

        return workflow

    def create_as_workflow(
        self,
        generate_name: Optional[str] = None,
        wait: bool = False,
        poll_interval: int = 5,
    ) -> TWorkflow:
        """Run this WorkflowTemplate instantly as a Workflow.

        If generate_name is given, the workflow created uses generate_name as a prefix, as per the usual for
        hera.workflows.Workflow.generate_name. If not given, the WorkflowTemplate's name will be used, truncated to 57
        chars and appended with a hyphen.

        Note: this function does not require the WorkflowTemplate to already exist on the cluster
        """
        workflow = self._get_as_workflow(generate_name)
        return workflow.create(wait=wait, poll_interval=poll_interval)


__all__ = ["WorkflowTemplate"]
