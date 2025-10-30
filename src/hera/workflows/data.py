"""The `hera.workflows.data` module provides Argo data functionality, such as sourcing data + applying transformations."""

from typing import List, Union

from hera.expr._node import Node
from hera.workflows import models as m
from hera.workflows._meta_mixins import CallableTemplateMixin
from hera.workflows._mixins import IOMixin, TemplateMixin
from hera.workflows.artifact import Artifact


class Data(TemplateMixin, IOMixin, CallableTemplateMixin):
    """`Data` implements the Argo data template representation.

    Data can be used to indicate that some data, identified by a `source`, should be processed via the specified
    `transformations`. The `transformations` field can be either expressed via a pure `str` or via a `hera.expr`,
    which transpiles the expression into a statement that can be processed by Argo.
    """

    source: Union[m.DataSource, m.ArtifactPaths, Artifact]
    transformations: List[Union[str, Node]] = []

    def _build_source(self) -> m.DataSource:
        """Builds the generated `DataSource`."""
        if isinstance(self.source, m.DataSource):
            return self.source
        elif isinstance(self.source, m.ArtifactPaths):
            return m.DataSource(artifact_paths=self.source)
        return m.DataSource(artifact_paths=self.source._build_artifact_paths())

    def _build_data(self) -> m.Data:
        """Builds the generated `Data` template."""
        return m.Data(
            source=self._build_source(),
            transformation=list(map(lambda expr: m.TransformationStep(expression=str(expr)), self.transformations)),
        )

    def _build_template(self) -> m.Template:
        """Builds the generated `Template` from the fields of `Data`."""
        return m.Template(
            active_deadline_seconds=self.active_deadline_seconds,
            affinity=self.affinity,
            archive_location=self.archive_location,
            automount_service_account_token=self.automount_service_account_token,
            data=self._build_data(),
            executor=self.executor,
            fail_fast=self.fail_fast,
            host_aliases=self.host_aliases,
            init_containers=self._build_init_containers(),
            inputs=self._build_inputs(),
            outputs=self._build_outputs(),
            memoize=self.memoize,
            metadata=self._build_metadata(),
            name=self.name,
            node_selector=self.node_selector,
            plugin=self.plugin,
            priority_class_name=self.priority_class_name,
            retry_strategy=self._build_retry_strategy(),
            scheduler_name=self.scheduler_name,
            security_context=self.pod_security_context,
            service_account_name=self.service_account_name,
            sidecars=self._build_sidecars(),
            synchronization=self.synchronization,
            timeout=self.timeout,
            tolerations=self.tolerations,
        )


__all__ = ["Data"]
