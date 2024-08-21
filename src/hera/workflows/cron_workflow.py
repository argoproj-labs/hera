"""The cron_workflow module provides the CronWorkflow class.

See https://argoproj.github.io/argo-workflows/cron-workflows
for more on CronWorkflows.
"""

from pathlib import Path
from typing import Dict, Optional, Type, Union, cast

from hera._utils import type_util
from hera.workflows._meta_mixins import ModelMapperMixin, _set_model_attr

try:
    from typing import Annotated  # type: ignore
except ImportError:
    from typing_extensions import Annotated  # type: ignore

from hera.exceptions import NotFound
from hera.shared._pydantic import BaseModel
from hera.workflows._meta_mixins import (
    _get_model_attr,
)
from hera.workflows.models import (
    CreateCronWorkflowRequest,
    CronWorkflow as _ModelCronWorkflow,
    CronWorkflowSpec,
    CronWorkflowStatus,
    LintCronWorkflowRequest,
    UpdateCronWorkflowRequest,
    Workflow as _ModelWorkflow,
)
from hera.workflows.protocol import TWorkflow
from hera.workflows.workflow import Workflow, _WorkflowModelMapper


class _CronWorkflowModelMapper(_WorkflowModelMapper):
    @classmethod
    def _get_model_class(cls) -> Type[BaseModel]:
        return _ModelCronWorkflow

    @classmethod
    def build_model(
        cls, hera_class: Type[ModelMapperMixin], hera_obj: ModelMapperMixin, model: TWorkflow
    ) -> TWorkflow:
        assert isinstance(hera_obj, ModelMapperMixin)

        for attr, annotation in hera_class._get_all_annotations().items():
            if type_util.is_annotated(annotation) and (
                mapper := type_util.consume_annotated_metadata(annotation, ModelMapperMixin.ModelMapper)
            ):
                if not isinstance(mapper, _CronWorkflowModelMapper) and mapper.model_path[0] == "spec":
                    # Skip attributes mapped to spec by parent _WorkflowModelMapper
                    continue

                # Value comes from builder function if it exists on hera_obj, otherwise directly from the attr
                value = (
                    getattr(hera_obj, mapper.builder.__name__)()
                    if mapper.builder is not None
                    else getattr(hera_obj, attr)
                )
                if value is not None:
                    _set_model_attr(model, mapper.model_path, value)

        return model


class CronWorkflow(Workflow):
    """CronWorkflow allows a user to run a Workflow on a recurring basis.

    Note:
        Hera's CronWorkflow is a subclass of Workflow which means certain fields are renamed
        for compatibility, see `cron_suspend` and `cron_status` which are different from the Argo
        spec. See [CronWorkflowSpec](https://argoproj.github.io/argo-workflows/fields/#cronworkflow) for more details.
    """

    concurrency_policy: Annotated[Optional[str], _CronWorkflowModelMapper("spec.concurrency_policy")] = None
    failed_jobs_history_limit: Annotated[Optional[int], _CronWorkflowModelMapper("spec.failed_jobs_history_limit")] = (
        None
    )
    schedule: Annotated[str, _CronWorkflowModelMapper("spec.schedule")]
    starting_deadline_seconds: Annotated[Optional[int], _CronWorkflowModelMapper("spec.starting_deadline_seconds")] = (
        None
    )
    successful_jobs_history_limit: Annotated[
        Optional[int], _CronWorkflowModelMapper("spec.successful_jobs_history_limit")
    ] = None
    cron_suspend: Annotated[Optional[bool], _CronWorkflowModelMapper("spec.suspend")] = None
    timezone: Annotated[Optional[str], _CronWorkflowModelMapper("spec.timezone")] = None
    cron_status: Annotated[Optional[CronWorkflowStatus], _CronWorkflowModelMapper("status")] = None

    def create(self) -> TWorkflow:  # type: ignore
        """Creates the CronWorkflow on the Argo cluster."""
        assert self.workflows_service, "workflow service not initialized"
        assert self.namespace, "workflow namespace not defined"

        wf = self.workflows_service.create_cron_workflow(
            CreateCronWorkflowRequest(cron_workflow=self.build()),  # type: ignore
            namespace=self.namespace,
        )
        # set the name on the object so that we can do a get/update later
        self.name = wf.metadata.name
        return wf

    def get(self) -> TWorkflow:
        """Attempts to get a cron workflow based on the parameters of this template e.g. name + namespace."""
        assert self.workflows_service, "workflow service not initialized"
        assert self.namespace, "workflow namespace not defined"
        assert self.name, "workflow name not defined"
        return self.workflows_service.get_cron_workflow(name=self.name, namespace=self.namespace)

    def update(self) -> TWorkflow:
        """Attempts to perform a workflow template update based on the parameters of this template.

        Note that this creates the template if it does not exist. In addition, this performs
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
        return self.workflows_service.update_cron_workflow(
            self.name,
            UpdateCronWorkflowRequest(cron_workflow=template),  # type: ignore
            namespace=self.namespace,
        )

    def lint(self) -> TWorkflow:
        """Lints the CronWorkflow using the Argo cluster."""
        assert self.workflows_service, "workflow service not initialized"
        assert self.namespace, "workflow namespace not defined"
        return self.workflows_service.lint_cron_workflow(
            LintCronWorkflowRequest(cron_workflow=self.build()),  # type: ignore
            namespace=self.namespace,
        )

    def build(self) -> TWorkflow:
        """Builds the CronWorkflow and its components into an Argo schema CronWorkflow object."""
        self = self._dispatch_hooks()

        model_workflow = cast(_ModelWorkflow, super().build())
        model_cron_workflow = _ModelCronWorkflow(
            metadata=model_workflow.metadata,
            spec=CronWorkflowSpec(
                schedule=self.schedule,
                workflow_spec=model_workflow.spec,
            ),
        )

        return _CronWorkflowModelMapper.build_model(CronWorkflow, self, model_cron_workflow)

    @classmethod
    def _from_model(cls, model: BaseModel) -> ModelMapperMixin:
        """Parse from given model to cls's type."""
        assert isinstance(model, _ModelCronWorkflow)
        hera_cron_workflow = cls(schedule="")

        for attr, annotation in cls._get_all_annotations().items():
            if type_util.is_annotated(annotation) and (
                mapper := type_util.consume_annotated_metadata(annotation, ModelMapperMixin.ModelMapper)
            ):
                if mapper.model_path:
                    value = None

                    if (
                        isinstance(mapper, _CronWorkflowModelMapper)
                        or isinstance(mapper, _WorkflowModelMapper)
                        and mapper.model_path[0] == "metadata"
                    ):
                        value = _get_model_attr(model, mapper.model_path)
                    elif isinstance(mapper, _WorkflowModelMapper) and mapper.model_path[0] == "spec":
                        # We map "spec.workflow_spec" from the model CronWorkflow to "spec" for Hera's Workflow (used
                        # as the parent class of Hera's CronWorkflow)
                        value = _get_model_attr(model.spec.workflow_spec, mapper.model_path[1:])

                    if value is not None:
                        setattr(hera_cron_workflow, attr, value)

        return hera_cron_workflow

    @classmethod
    def from_dict(cls, model_dict: Dict) -> ModelMapperMixin:
        """Create a CronWorkflow from a CronWorkflow contained in a dict.

        Examples:
            >>> my_cron_workflow = CronWorkflow(name="my-cron-wf")
            >>> my_cron_workflow == CronWorkflow.from_dict(my_cron_workflow.to_dict())
            True
        """
        return cls._from_dict(model_dict, _ModelCronWorkflow)

    @classmethod
    def from_yaml(cls, yaml_str: str) -> ModelMapperMixin:
        """Create a CronWorkflow from a CronWorkflow contained in a YAML string.

        Examples:
            >>> my_cron_workflow = CronWorkflow.from_yaml(yaml_str)
        """
        return cls._from_yaml(yaml_str, _ModelCronWorkflow)

    @classmethod
    def from_file(cls, yaml_file: Union[Path, str]) -> ModelMapperMixin:
        """Create a CronWorkflow from a CronWorkflow contained in a YAML file.

        Examples:
            >>> yaml_file = Path(...)
            >>> my_workflow_template = CronWorkflow.from_file(yaml_file)
        """
        return cls._from_file(yaml_file, _ModelCronWorkflow)

    def get_workflow_link(self) -> str:
        """Returns the workflow link for the workflow."""
        assert self.workflows_service is not None, "Cannot fetch a cron workflow link without a service"
        assert self.name is not None, "Cannot fetch a cron workflow link without a cron workflow name"
        return self.workflows_service.get_cron_workflow_link(self.name)


__all__ = ["CronWorkflow"]
