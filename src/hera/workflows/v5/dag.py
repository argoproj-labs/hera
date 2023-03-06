from __future__ import annotations

from typing import Any, List, Optional, Union

from hera.workflows.models import (
    DAGTask,
    DAGTemplate as _ModelDAGTemplate,
    Template as _ModelTemplate,
)
from hera.workflows.v5._mixins import _ContextMixin, _IOMixin, _SubNodeMixin, _TemplateMixin
from hera.workflows.v5.task import Task


class DAG(_IOMixin, _TemplateMixin, _SubNodeMixin, _ContextMixin):
    fail_fast: Optional[bool] = None
    target: Optional[str] = None
    tasks: List[Union[Task, DAGTask]] = []

    def _add_sub(self, node: Any):
        self.tasks.append(node)

    def _build_dag_template(self) -> _ModelDAGTemplate:
        tasks = []
        for task in self.tasks:
            if isinstance(task, Task):
                tasks.append(task._build_dag_task())
            else:
                tasks.append(task)
        return _ModelDAGTemplate(fail_fast=self.fail_fast, target=self.target, tasks=tasks)

    def _build_template(self) -> _ModelTemplate:
        return _ModelTemplate(
            active_deadline_seconds=self.active_deadline_seconds,
            affinity=self.affinity,
            archive_location=self.archive_location,
            automount_service_account_token=self.automount_service_account_token,
            container=None,
            container_set=None,
            daemon=self.daemon,
            dag=self._build_dag_template(),
            data=None,
            executor=self.executor,
            fail_fast=self.fail_fast,
            host_aliases=self.host_aliases,
            http=None,
            init_containers=self.init_containers,
            inputs=self._build_inputs(),
            memoize=self.memoize,
            metadata=self._build_metadata(),
            metrics=self.metrics,
            name=self.name,
            node_selector=self.node_selector,
            outputs=self._build_outputs(),
            parallelism=self.paralellism,
            plugin=self.plugin,
            pod_spec_patch=self.pod_spec_patch,
            priority=self.priority,
            priority_class_name=self.priority_class_name,
            resource=None,
            retry_strategy=self.retry_strategy,
            scheduler_name=self.scheduler_name,
            script=None,
            security_context=self.pod_security_context,
            service_account_name=self.service_account_name,
            sidecars=self.sidecars,
            steps=None,
            suspend=None,
            synchronization=self.synchronization,
            timeout=self.timeout,
            tolerations=self.tolerations,
        )
