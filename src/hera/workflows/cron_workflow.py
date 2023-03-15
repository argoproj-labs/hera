from __future__ import annotations

from types import ModuleType
from typing import Any, Dict, Optional

from pydantic import validator
from typing_extensions import get_args

from hera.shared.global_config import GlobalConfig
from hera.workflows._mixins import ContextMixin
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
# from hera.workflows.workflow_spec import WorkflowSpec

_yaml: Optional[ModuleType] = None
try:
    import yaml

    _yaml = yaml
except ImportError:
    _yaml = None


class CronWorkflow(ContextMixin):
    api_version: Optional[str] = GlobalConfig.api_version
    kind: Optional[str] = None
    annotations: Optional[Dict[str, str]] = None

    concurrency_policy: Optional[str] = None
    failed_jobs_history_limit: Optional[int] = None
    schedule: str
    starting_deadline_seconds: Optional[int] = None
    successful_jobs_history_limit: Optional[int] = None
    suspend: Optional[bool] = None
    timezone: Optional[str] = None
    status: Optional[CronWorkflowStatus] = None
    # workflow_spec: WorkflowSpec = WorkflowSpec()
    workflows_service: Optional[WorkflowsService] = None

    @validator("workflows_service", pre=True, always=True)
    def _set_workflows_service(cls, v):
        if v is None:
            return WorkflowsService()
        return v

    @validator("kind", pre=True, always=True)
    def _set_kind(cls, v):
        if v is None:
            return cls.__name__  # type: ignore
        return v

    def _add_sub(self, node: Any):
        if not isinstance(node, (Templatable, *get_args(Template))):
            raise InvalidType()
        self.workflow.templates.append(node)

    def build(self) -> _ModelCronWorkflow:
        pass
        # return _ModelCronWorkflow(
        #     api_version=self.api_version,
        #     kind=self.kind,
        #     metadata=ObjectMeta(
        #         annotations=self.annotations,
        #         cluster_name=self.cluster_name,
        #         creation_timestamp=self.creation_timestamp,
        #         deletion_grace_period_seconds=self.deletion_grace_period_seconds,
        #         deletion_timestamp=self.deletion_timestamp,
        #         finalizers=self.finalizers,
        #         generate_name=self.generate_name,
        #         generation=self.generation,
        #         labels=self.labels,
        #         managed_fields=self.managed_fields,
        #         name=self.name,
        #         namespace=self.namespace,
        #         owner_references=self.owner_references,
        #         resource_version=self.resource_version,
        #         self_link=self.self_link,
        #         uid=self.uid,
        #     ),
        #     spec=CronWorkflowSpec(
        #         concurrency_policy=self.concurrency_policy,
        #         failed_jobs_history_limit=self.failed_jobs_history_limit,
        #         schedule=self.schedule,
        #         starting_deadline_seconds=self.starting_deadline_seconds,
        #         successful_jobs_history_limit=self.successful_jobs_history_limit,
        #         suspend=self.suspend,
        #         timezone=self.timezone,
        #         workflow_metadata=None,
        #         workflow_spec=self.workflow_spec.build(),
        #     ),
        #     status=self.status,
        # )

    def to_dict(self) -> Any:
        return self.build().dict(exclude_none=True, by_alias=True)

    def to_yaml(self, *args, **kwargs) -> str:
        if not yaml:
            raise ImportError("PyYAML is not installed")
        return yaml.dump(self.to_dict(), *args, **kwargs)
    
    def _add_sub(self, node: Any):
        pass


__all__ = ["CronWorkflow"]
