"""The `hera.workflows.dag` module provides the DAG class.

See <https://argoproj.github.io/argo-workflows/walk-through/dag>
for more on DAGs (Directed Acyclic Graphs) in Argo Workflows.
"""

from __future__ import annotations

from typing import Any, List, Optional, Set, Union

from hera.shared._pydantic import PrivateAttr
from hera.workflows._context import _context
from hera.workflows._meta_mixins import CallableTemplateMixin, ContextMixin
from hera.workflows._mixins import IOMixin, TemplateMixin
from hera.workflows.exceptions import InvalidType, NodeNameConflict
from hera.workflows.models import (
    DAGTask,
    DAGTemplate as _ModelDAGTemplate,
    Template as _ModelTemplate,
)
from hera.workflows.protocol import Templatable
from hera.workflows.task import Task


class DAG(
    IOMixin,
    TemplateMixin,
    CallableTemplateMixin,
    ContextMixin,
):
    """A DAG template invocator is used to define Task dependencies as an acyclic graph.

    DAG implements the contextmanager interface so allows usage of `with`, under which any Task
    objects instantiated will be added to the DAG's list of Tasks.

    See the [DAG examples](../../../examples/workflows/dags/dag_diamond_with_script.md) for usage.
    """

    fail_fast: Optional[bool] = None
    target: Optional[str] = None
    tasks: List[Union[Task, DAGTask]] = []

    _node_names = PrivateAttr(default_factory=set)
    _current_task_depends: Set[str] = PrivateAttr(set())

    def _add_sub(self, node: Any):
        if isinstance(node, Templatable):
            from hera.workflows.workflow import Workflow

            # We must be under a workflow context due to checks in _HeraContext.add_sub_node
            assert _context.pieces and isinstance(_context.pieces[0], Workflow)
            _context.pieces[0]._add_sub(node)
            return

        if not isinstance(node, Task):
            raise InvalidType(type(node))
        if node.name in self._node_names:
            raise NodeNameConflict(f"Found multiple Task nodes with name: {node.name}")
        self._node_names.add(node.name)
        self.tasks.append(node)

    def _build_template(self) -> _ModelTemplate:
        """Builds the auto-generated `Template` representation of the `DAG`."""
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
            retry_strategy=self._build_retry_strategy(),
            scheduler_name=self.scheduler_name,
            security_context=self.pod_security_context,
            service_account_name=self.service_account_name,
            sidecars=self._build_sidecars(),
            synchronization=self.synchronization,
            timeout=self.timeout,
            tolerations=self.tolerations,
        )


__all__ = ["DAG"]
