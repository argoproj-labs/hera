from hera.workflows.operator import Operator
from hera.workflows.task import Task, TaskResult


def test_task_rshift():
    task_a = Task(name="task-a", template="dummy")
    task_b = Task(name="task-b", template="dummy")

    task_a >> task_b

    assert task_b.depends == "task-a"


def test_override_task_next_success_only():
    task_a = Task(name="task-a", template="dummy")
    task_b = Task(name="task-b", template="dummy")

    with Task.set_next_defaults(on=TaskResult.succeeded):
        task_a >> task_b

    assert task_b.depends == "task-a.Succeeded"


def test_override_task_next_operator_or():
    task_a = Task(name="task-a", template="dummy")
    task_b = Task(name="task-b", template="dummy")
    task_c = Task(name="task-c", template="dummy")

    with Task.set_next_defaults(operator=Operator.or_):
        [task_a, task_b] >> task_c

    assert task_c.depends == "task-a || task-b"


def test_override_task_next_operator_or_success_only():
    task_a = Task(name="task-a", template="dummy")
    task_b = Task(name="task-b", template="dummy")
    task_c = Task(name="task-c", template="dummy")

    with Task.set_next_defaults(operator=Operator.or_, on=TaskResult.succeeded):
        [task_a, task_b] >> task_c

    assert task_c.depends == "task-a.Succeeded || task-b.Succeeded"
