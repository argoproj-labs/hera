from typing import List, Union

from hera.expr._node import Node
from hera.workflows import models as m
from hera.workflows.v5._mixins import IOMixin, TemplateMixin


class Data(TemplateMixin, IOMixin):
    artifact_paths: m.ArtifactPaths
    transformations: List[Union[str, Node]] = []

    def _build_data(self) -> m.Data:
        return m.Data(
            source=m.DataSource(artifact_paths=self.artifact_paths),
            transformation=list(map(lambda expr: m.TransformationStep(expression=str(expr)), self.transformations)),
        )

    def _build_template(self) -> m.Template:
        return m.Template(
            active_deadline_seconds=self.active_deadline_seconds,
            affinity=self.affinity,
            archive_location=self.archive_location,
            automount_service_account_token=self.automount_service_account_token,
            data=self._build_data(),
            executor=self.executor,
            fail_fast=self.fail_fast,
            host_aliases=self.host_aliases,
            init_containers=self.init_containers,
            inputs=self._build_inputs(),
            outputs=self._build_outputs(),
            memoize=self.memoize,
            metadata=self._build_metadata(),
            name=self.name,
            node_selector=self.node_selector,
            plugin=self.plugin,
            priority=self.priority,
            priority_class_name=self.priority_class_name,
            retry_strategy=self.retry_strategy,
            scheduler_name=self.scheduler_name,
            security_context=self.pod_security_context,
            service_account_name=self.service_account_name,
            sidecars=self.sidecars,
            synchronization=self.synchronization,
            timeout=self.timeout,
            tolerations=self.tolerations,
        )
