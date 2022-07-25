from __future__ import annotations

from typing import TYPE_CHECKING, Union

from hera.task import Task

if TYPE_CHECKING:
    from hera.cron_workflow import CronWorkflow
    from hera.workflow import Workflow
    from hera.workflow_template import WorkflowTemplate


def add_task(w: Union["WorkflowTemplate", "CronWorkflow", "Workflow"], t: Task) -> None:
    """Adds a single task to the workflow"""
    add_tasks(w, t)


def add_tasks(w: Union["WorkflowTemplate", "CronWorkflow", "Workflow"], *ts: Task) -> None:
    """Adds multiple tasks to the workflow"""
    if not all(ts):
        return

    for t in ts:
        w.tasks.append(t)
