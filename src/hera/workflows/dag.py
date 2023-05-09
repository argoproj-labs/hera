"""The dag module provides the DAG class.

See https://argoproj.github.io/argo-workflows/walk-through/dag/
for more on DAGs (Directed Acyclic Graphs).
"""
from __future__ import annotations

from typing import Any, List, Optional, Union

from hera.workflows._mixins import CallableTemplateMixin, ContextMixin, IOMixin, TemplateMixin
from hera.workflows.exceptions import InvalidType
from hera.workflows.models import (
    DAGTask,
    DAGTemplate as _ModelDAGTemplate,
    Template as _ModelTemplate,
)
from hera.workflows.task import Task


class DAG(IOMixin, TemplateMixin, CallableTemplateMixin, ContextMixin):
    """A DAG template invocator is used to define Task dependencies as an acyclic graph.

    DAG implements the contextmanager interface so allows usage of `with`, under which any
    `hera.workflows.task.Task` objects instantiated will be added to the DAG's list of Tasks.
    """

    fail_fast: Optional[bool] = None
    target: Optional[str] = None
    tasks: List[Union[Task, DAGTask]] = []

    def _add_sub(self, node: Any):
        if not isinstance(node, Task):
            raise InvalidType(type(node))
        self.tasks.append(node)

    def _build_template(self) -> _ModelTemplate:
        tasks = []
        for task in self.tasks:
            if isinstance(task, Task):
                tasks.append(task._build_dag_task())
            else:
                tasks.append(task)
        return _ModelTemplate(
            active_deadline_seconds=self.active_deadline_seconds,
            affinity=self.affinity,
            archive_location=self.archive_location,
            automount_service_account_token=self.automount_service_account_token,
            daemon=self.daemon,
            dag=_ModelDAGTemplate(fail_fast=self.fail_fast, target=self.target, tasks=tasks),
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
            retry_strategy=self.retry_strategy,
            scheduler_name=self.scheduler_name,
            security_context=self.pod_security_context,
            service_account_name=self.service_account_name,
            sidecars=self._build_sidecars(),
            synchronization=self.synchronization,
            timeout=self.timeout,
            tolerations=self.tolerations,
        )


__all__ = ["DAG"]
