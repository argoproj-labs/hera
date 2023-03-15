from __future__ import annotations

from types import ModuleType
from typing import Any, Dict, Optional

from pydantic import validator
from typing_extensions import get_args

from hera.shared.global_config import GlobalConfig
from hera.workflows.exceptions import InvalidType
from hera.workflows.models import (
    CronWorkflow as _ModelCronWorkflow,
    CronWorkflowSpec,
    CronWorkflowStatus,
    ObjectMeta,
    Template,
)
from hera.workflows.protocol import Templatable
from hera.workflows.service import WorkflowsService
from hera.workflows.workflow import Workflow

_yaml: Optional[ModuleType] = None
try:
    import yaml

    _yaml = yaml
except ImportError:
    _yaml = None


class CronWorkflow(Workflow):
    concurrency_policy: Optional[str] = None
    failed_jobs_history_limit: Optional[int] = None
    schedule: str
    starting_deadline_seconds: Optional[int] = None
    successful_jobs_history_limit: Optional[int] = None
    cron_suspend: Optional[bool] = None
    timezone: Optional[str] = None
    cron_status: Optional[CronWorkflowStatus] = None

    def build(self) -> _ModelCronWorkflow:
        return _ModelCronWorkflow(
            api_version=self.api_version,
            kind=self.kind,
            metadata=ObjectMeta(
                annotations=self.annotations,
                cluster_name=self.cluster_name,
                creation_timestamp=self.creation_timestamp,
                deletion_grace_period_seconds=self.deletion_grace_period_seconds,
                deletion_timestamp=self.deletion_timestamp,
                finalizers=self.finalizers,
                generate_name=self.generate_name,
                generation=self.generation,
                labels=self.labels,
                managed_fields=self.managed_fields,
                name=self.name,
                namespace=self.namespace,
                owner_references=self.owner_references,
                resource_version=self.resource_version,
                self_link=self.self_link,
                uid=self.uid,
            ),
            spec=CronWorkflowSpec(
                concurrency_policy=self.concurrency_policy,
                failed_jobs_history_limit=self.failed_jobs_history_limit,
                schedule=self.schedule,
                starting_deadline_seconds=self.starting_deadline_seconds,
                successful_jobs_history_limit=self.successful_jobs_history_limit,
                suspend=self.cron_suspend,
                timezone=self.timezone,
                workflow_metadata=None,
                workflow_spec=super().build().spec,
            ),
            status=self.status,
        )


__all__ = ["CronWorkflow"]
