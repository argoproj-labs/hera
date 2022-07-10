import threading
from typing import Optional, Union

from hera.cron_workflow import CronWorkflow
from hera.task import Task
from hera.workflow import Workflow
from hera.workflow_template import WorkflowTemplate


class _Context(threading.local):
    def __init__(self) -> None:
        super().__init__()
        self._workflow: Optional[Union[Workflow, CronWorkflow, WorkflowTemplate]] = None

    def set(self, w: Union[Workflow, CronWorkflow, WorkflowTemplate]) -> None:
        if self._workflow is not None:
            raise ValueError(f"Hera context already defined with workflow: {self._workflow}")
        self._workflow = w

    def reset(self) -> None:
        self._workflow = None

    def is_set(self) -> bool:
        return self._workflow is not None

    def add_task(self, t: Task) -> None:
        self._workflow.add_task(t)

    def add_tasks(self, *ts: Task) -> None:
        self._workflow.add_tasks(*ts)


context = _Context()
