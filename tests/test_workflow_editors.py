from hera import Task, Workflow
from hera.workflow_editors import pre_create_cleanup


def test_pre_create_cleanup_trims_exit_tasks(ws):
    with Workflow('w', service=ws) as w:
        Task('t').on_exit(Task('e'))
    pre_create_cleanup(w)

    assert len(w.dag_template.tasks) == 1  # only a single task
    assert len(w.spec.templates) == 3  # the workflow, dag, and exit task


def test_pre_create_cleanup_does_not_affect_workflows_when_no_exit_task_specified(ws):
    with Workflow('w', service=ws) as w:
        Task('t')
    pre_create_cleanup(w)

    assert len(w.dag_template.tasks) == 1  # only a single task
    assert len(w.spec.templates) == 2  # the workflow, and dag
