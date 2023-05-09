from typing import List, Optional, Union

from hera.workflows._mixins import CallableTemplateMixin, IOMixin, SubNodeMixin, TemplateMixin
from hera.workflows.cron_workflow import CronWorkflow
from hera.workflows.models import (
    ManifestFrom,
    ResourceTemplate as _ModelResourceTemplate,
    Template as _ModelTemplate,
)
from hera.workflows.workflow import Workflow
from hera.workflows.workflow_template import WorkflowTemplate


class Resource(CallableTemplateMixin, TemplateMixin, SubNodeMixin, IOMixin):
    action: str
    failure_condition: Optional[str] = None
    flags: Optional[List[str]] = None
    manifest: Optional[Union[str, Workflow, CronWorkflow, WorkflowTemplate]] = None
    manifest_from: Optional[ManifestFrom] = None
    merge_strategy: Optional[str] = None
    set_owner_reference: Optional[bool] = None
    success_condition: Optional[str] = None

    def _build_manifest(self) -> Optional[str]:
        if isinstance(self.manifest, (Workflow, CronWorkflow, WorkflowTemplate)):
            # hack to appease raw yaml string comparison
            return self.manifest.to_yaml().replace("'{{", "{{").replace("}}'", "}}")
        return self.manifest

    def _build_resource_template(self) -> _ModelResourceTemplate:
        return _ModelResourceTemplate(
            action=self.action,
            failure_condition=self.failure_condition,
            flags=self.flags,
            manifest=self._build_manifest(),
            manifest_from=self.manifest_from,
            merge_strategy=self.merge_strategy,
            set_owner_reference=self.set_owner_reference,
            success_condition=self.success_condition,
        )

    def _build_template(self) -> _ModelTemplate:
        return _ModelTemplate(
            active_deadline_seconds=self.active_deadline_seconds,
            affinity=self.affinity,
            archive_location=self.archive_location,
            automount_service_account_token=self.automount_service_account_token,
            daemon=self.daemon,
            executor=self.executor,
            fail_fast=self.fail_fast,
            host_aliases=self.host_aliases,
            init_containers=self.init_containers,
            inputs=self._build_inputs(),
            memoize=self.memoize,
            metadata=self._build_metadata(),
            metrics=self._build_metrics(),
            name=self.name,
            node_selector=self.node_selector,
            outputs=self._build_outputs(),
            parallelism=self.parallelism,
            plugin=self.plugin,
            pod_spec_patch=self.pod_spec_patch,
            priority=self.priority,
            priority_class_name=self.priority_class_name,
            resource=self._build_resource_template(),
            retry_strategy=self.retry_strategy,
            scheduler_name=self.scheduler_name,
            security_context=self.pod_security_context,
            service_account_name=self.service_account_name,
            sidecars=self._build_sidecars(),
            synchronization=self.synchronization,
            timeout=self.timeout,
            tolerations=self.tolerations,
        )


__all__ = ["Resource"]
