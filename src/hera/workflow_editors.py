from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hera.workflow import Workflow
    from hera.cron_workflow import CronWorkflow
    from hera.workflow_template import WorkflowTemplate

from typing import Union

from hera.task import Task
from hera.volumes import Volume


def add_task(w: Union['WorkflowTemplate', 'CronWorkflow', 'Workflow'], t: Task) -> None:
    """Adds a single task to the workflow"""
    add_tasks(w, t)


def add_tasks(w: Union['WorkflowTemplate', 'CronWorkflow', 'Workflow'], *ts: Task) -> None:
    """Adds multiple tasks to the workflow"""
    if not all(ts):
        return

    for t in ts:
        w.spec.templates.append(t.argo_template)

        if t.resources.volumes:
            for vol in t.resources.volumes:
                if isinstance(vol, Volume):
                    # dynamically provisioned volumes need associated claims on the workflow spec
                    w.spec.volume_claim_templates.append(vol.get_claim_spec())
                else:
                    w.spec.volumes.append(vol.get_volume())

        w.dag_template.tasks.append(t.argo_task)


def add_head(w: Union['WorkflowTemplate', 'CronWorkflow', 'Workflow'], t: Task, append: bool = True) -> None:
    """Adds a task at the head of the workflow so the workflow start with the given task.

    This sets the given task as a dependency of the starting tasks of the workflow.

    Parameters
    ----------
    t: Task
        The task to add to the head of the workflow.
    append: bool = True
        Whether to append the given task to the workflow.
    """
    if append:
        add_task(w, t)

    for template_task in w.dag_template.tasks:
        if template_task.name != t.name:
            if hasattr(template_task, 'dependencies'):
                template_task.dependencies.append(t.name)
            else:
                setattr(template_task, 'dependencies', [t.name])


def add_tail(w: Union['WorkflowTemplate', 'CronWorkflow', 'Workflow'], t: Task, append: bool = True) -> None:
    """Adds a task as the tail of the workflow so the workflow ends with the given task.

    This sets the given task's dependencies to all the tasks that are not listed as dependencies in the workflow.

    Parameters
    ----------
    t: Task
        The task to add to the tail of the workflow.
    append: bool = True
        Whether to append the given task to the workflow.
    """
    if append:
        add_task(w, t)

    dependencies = set()
    task_name_to_task = dict()
    for template_task in w.dag_template.tasks:
        if hasattr(template_task, 'dependencies'):
            dependencies.update(template_task.dependencies)
        if template_task.name != t.name:
            task_name_to_task[template_task.name] = template_task

    # the tasks that are not listed as dependencies are "end tasks" i.e nothing follows after
    # e.g if A -> B -> C then B.deps = [A] and C.deps = [B] but nothing lists C so C is "free"
    free_tasks = set(task_name_to_task.keys()).difference(dependencies)
    t.argo_task.dependencies = list(free_tasks)
