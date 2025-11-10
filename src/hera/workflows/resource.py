"""The `hera.workflows.resource` module provides functionality for creating K8s resources via workflows inside task/steps."""

from typing import TYPE_CHECKING, List, Optional, Union

from hera.workflows._meta_mixins import CallableTemplateMixin
from hera.workflows._mixins import IOMixin, SubNodeMixin, TemplateMixin
from hera.workflows.models import (
    ManifestFrom,
    ResourceTemplate as _ModelResourceTemplate,
    Template as _ModelTemplate,
)

if TYPE_CHECKING:
    from hera.workflows.cron_workflow import CronWorkflow
    from hera.workflows.workflow import Workflow
    from hera.workflows.workflow_template import WorkflowTemplate


class Resource(CallableTemplateMixin, TemplateMixin, SubNodeMixin, IOMixin):
    """`Resource` is a representation of a K8s resource that can be created by Argo.

    The resource is a callable step that can be invoked in a DAG/Workflow. The resource can create any K8s resource,
    such as other workflows, workflow templates, daemons, etc, as specified by the `manifest` field of the resource.
    The manifest field is a canonical YAML that is submitted to K8s by Argo. Note that the manifest is a union of
    multiple types. The manifest can be a string, in which case it is assume to be YAML. Otherwise, if it's a Hera
    objects, it is automatically converted to the corresponding YAML representation.
    """

    action: str
    failure_condition: Optional[str] = None
    flags: Optional[List[str]] = None
    manifest: Optional[Union[str, "Workflow", "CronWorkflow", "WorkflowTemplate"]] = None
    manifest_from: Optional[ManifestFrom] = None
    merge_strategy: Optional[str] = None
    set_owner_reference: Optional[bool] = None
    success_condition: Optional[str] = None

    def __new__(cls, *args, **kwargs) -> "Resource":
        """Importing here to avoid circular imports."""
        from hera.workflows.cron_workflow import CronWorkflow
        from hera.workflows.workflow import Workflow
        from hera.workflows.workflow_template import WorkflowTemplate

        cls.update_forward_refs(Workflow=Workflow, CronWorkflow=CronWorkflow, WorkflowTemplate=WorkflowTemplate)

        instance = super().__new__(cls)
        return instance

    def _build_manifest(self) -> Optional[str]:
        from hera.workflows.cron_workflow import CronWorkflow
        from hera.workflows.workflow import Workflow
        from hera.workflows.workflow_template import WorkflowTemplate

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
            init_containers=self._build_init_containers(),
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
            priority_class_name=self.priority_class_name,
            resource=self._build_resource_template(),
            retry_strategy=self._build_retry_strategy(),
            scheduler_name=self.scheduler_name,
            security_context=self.pod_security_context,
            service_account_name=self.service_account_name,
            sidecars=self._build_sidecars(),
            synchronization=self.synchronization,
            timeout=self.timeout,
            tolerations=self.tolerations,
        )


__all__ = ["Resource"]
