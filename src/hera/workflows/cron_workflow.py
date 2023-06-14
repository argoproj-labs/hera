"""The cron_workflow module provides the CronWorkflow class

See https://argoproj.github.io/argo-workflows/cron-workflows
for more on CronWorkflows.
"""
from typing import Optional, Type

try:
    from typing import Annotated, get_args, get_origin
except ImportError:
    from typing_extensions import Annotated, get_args, get_origin  # type: ignore

from hera.shared._base_model import BaseModel
from hera.workflows._mixins import (
    ParseFromYamlMixin,
    _model_attr_setter,
)
from hera.workflows.models import (
    CreateCronWorkflowRequest,
    CronWorkflow as _ModelCronWorkflow,
    CronWorkflowSpec,
    CronWorkflowStatus,
    LintCronWorkflowRequest,
    ObjectMeta,
)
from hera.workflows.protocol import TWorkflow
from hera.workflows.workflow import Workflow, _WorkflowModelMapper


class _CronWorkflowModelMapper(_WorkflowModelMapper):
    @classmethod
    def _get_model_class(cls) -> Type[BaseModel]:
        return _ModelCronWorkflow

    @classmethod
    def build_model(
        cls, hera_class: Type[ParseFromYamlMixin], hera_obj: ParseFromYamlMixin, model: TWorkflow
    ) -> TWorkflow:
        assert isinstance(hera_obj, ParseFromYamlMixin)

        for attr, annotation in hera_class._get_all_annotations().items():
            if get_origin(annotation) is Annotated and isinstance(
                get_args(annotation)[1], ParseFromYamlMixin.ModelMapper
            ):
                mapper = get_args(annotation)[1]
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
                    _model_attr_setter(mapper.model_path, model, value)

        return model


class CronWorkflow(Workflow):
    """CronWorkflow allows a user to run a Workflow on a recurring basis.

    NB: Hera's CronWorkflow is a subclass of Workflow which means certain fields are renamed
    for compatibility, see `cron_suspend` and `cron_status` which are different from the Argo
    spec. See https://argoproj.github.io/argo-workflows/fields/#cronworkflow
    """

    concurrency_policy: Annotated[Optional[str], _CronWorkflowModelMapper("spec.concurrency_policy")] = None
    failed_jobs_history_limit: Annotated[
        Optional[int], _CronWorkflowModelMapper("spec.failed_jobs_history_limit")
    ] = None
    schedule: Annotated[str, _CronWorkflowModelMapper("spec.schedule")]
    starting_deadline_seconds: Annotated[
        Optional[int], _CronWorkflowModelMapper("spec.starting_deadline_seconds")
    ] = None
    successful_jobs_history_limit: Annotated[
        Optional[int], _CronWorkflowModelMapper("spec.successful_jobs_history_limit")
    ] = None
    cron_suspend: Annotated[Optional[bool], _CronWorkflowModelMapper("spec.suspend")] = None
    timezone: Annotated[Optional[str], _CronWorkflowModelMapper("spec.timezone")] = None
    cron_status: Annotated[Optional[CronWorkflowStatus], _CronWorkflowModelMapper("status")] = None

    def build(self) -> TWorkflow:
        """Builds the CronWorkflow and its components into an Argo schema CronWorkflow object."""
        self = self._dispatch_hooks()

        model_workflow = _ModelCronWorkflow(
            metadata=ObjectMeta(),
            spec=CronWorkflowSpec(
                schedule="",
                workflow_spec=super().build().spec,
            ),
        )

        return _CronWorkflowModelMapper.build_model(CronWorkflow, self, model_workflow)

    def create(self) -> TWorkflow:  # type: ignore
        """Creates the CronWorkflow on the Argo cluster."""
        assert self.workflows_service, "workflow service not initialized"
        assert self.namespace, "workflow namespace not defined"
        return self.workflows_service.create_cron_workflow(
            CreateCronWorkflowRequest(cron_workflow=self.build()), namespace=self.namespace
        )

    def lint(self) -> TWorkflow:
        """Lints the CronWorkflow using the Argo cluster."""
        assert self.workflows_service, "workflow service not initialized"
        assert self.namespace, "workflow namespace not defined"
        return self.workflows_service.lint_cron_workflow(
            LintCronWorkflowRequest(cron_workflow=self.build()), namespace=self.namespace
        )


__all__ = ["CronWorkflow"]
