import threading
from typing import List

from hera.dag import DAG
from hera.task import Task


class _DAG_context(threading.local):
    """Holds the directed acyclic graph context of a Hera workflow"""

    def __init__(self) -> None:
        super().__init__()
        self._dags: List[DAG] = []

    def enter(self, d: DAG) -> None:
        """Inject a DAG into the overall Hera DAG context"""
        self._dags.append(d)

    def exit(self) -> None:
        """Eject a DAG off the overall Hera DAG context"""
        self._dags.pop()

    def is_set(self) -> bool:
        """Return whether there are any DAGs set on the Hera DAG context"""
        return self._dags != []

    def add_task(self, t: Task) -> None:
        """Add a task to the DAG that was added last to the context"""
        self._dags[-1].add_task(t)

    def add_tasks(self, *ts: Task) -> None:
        """Adds a collection of tasks to the DAG that was added last to the context"""
        self._dags[-1].add_tasks(*ts)


dag_context = _DAG_context()
