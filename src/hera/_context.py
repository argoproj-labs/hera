import threading
from typing import List

from hera.dag import DAG
from hera.task import Task


class _DAG_context(threading.local):
    def __init__(self) -> None:
        super().__init__()
        self._dag: List[DAG] = []

    def enter(self, d: DAG) -> None:
        self._dag.append(d)

    def exit(self) -> None:
        self._dag.pop()

    def is_set(self) -> bool:
        return self._dag != []

    def add_task(self, t: Task) -> None:
        self._dag[-1].add_task(t)

    def add_tasks(self, *ts: Task) -> None:
        self._dag[-1].add_tasks(*ts)


dag_context = _DAG_context()
