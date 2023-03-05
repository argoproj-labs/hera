from __future__ import annotations

from typing import Any, List, Optional

from hera.workflows.models import (
    DAGTask,
    DAGTemplate as _ModelDAGTemplate,
    Template as _ModelTemplate,
)
from hera.workflows.v5._mixins import _DAGTaskMixin, _IOMixin, _TemplateMixin


class DAG(_IOMixin, _TemplateMixin):
    name: str
    fail_fast: Optional[bool] = None
    target: Optional[str] = None
    tasks: List[DAGTask] = []
    _task_queue: List[_DAGTaskMixin] = []

    def __enter__(self) -> DAG:
        """Enter the context of the workflow"""
        from hera.workflows.v5._context import _context

        _context.enter(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        from hera.workflows.v5._context import _context

        for task in self._task_queue:
            self.tasks.append(task._build_dag_task())

        _context.exit()

    def _add_sub(self, node: Any):
        self.add_task(node)

    def add_task(self, task: _DAGTaskMixin) -> None:
        self._task_queue.append(task)

    def _build_template(self) -> _ModelTemplate:
        return _ModelTemplate(
            active_deadline_seconds=self.active_deadline_seconds,
            affinity=self.affinity,
            archive_location=self.archive_location,
            automount_service_account_token=self.automount_service_account_token,
            daemon=self.daemon,
            dag=_ModelDAGTemplate(fail_fast=self.fail_fast, target=self.target, tasks=self.tasks),
            executor=self.executor,
            fail_fast=self.fail_fast,
            host_aliases=self.host_aliases,
            init_containers=self.init_containers,
            inputs=self._build_inputs(),
            memoize=self.memoize,
            metadata=self._build_metadata(),
            metrics=self.metrics,
            name=self.name,
            node_selector=self.node_selector,
            outputs=self._build_outputs(),
            plugin=self.plugin,
            pod_spec_patch=self.pod_spec_patch,
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
