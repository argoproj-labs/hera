"""The cron_workflow module provides the CronWorkflow class

See https://argoproj.github.io/argo-workflows/cron-workflows
for more on CronWorkflows.
"""
from __future__ import annotations

from typing import Optional, Type

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated

from hera.workflows.models import (
    CreateCronWorkflowRequest,
    CronWorkflow as _ModelCronWorkflow,
    CronWorkflowSpec,
    CronWorkflowStatus,
    LintCronWorkflowRequest,
    ObjectMeta,
)
from hera.workflows.protocol import TWorkflow
from hera.workflows.workflow import _WorkflowModelMapper, Workflow

class _CronWorkflowModelMapper(_WorkflowModelMapper):
    @classmethod
    def _get_model_class(cls) -> Type[_ModelCronWorkflow]:
        return _ModelCronWorkflow

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

    entrypoint: Annotated[Optional[str], _WorkflowModelMapper("workflow_spec.entrypoint")] = None


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

        return _CronWorkflowModelMapper.build_model(self, model_workflow)

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
