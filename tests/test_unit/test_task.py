from hera.workflows.operator import Operator
from hera.workflows.task import Task, TaskResult


def test_task_rshift():
    task_a = Task(name="task-a", template="dummy")
    task_b = Task(name="task-b", template="dummy")

    task_a >> task_b

    assert task_b.depends == "task-a"


def test_task_or_for_depends():
    task_a = Task(name="task-a", template="dummy")
    task_b = Task(name="task-b", template="dummy")
    task_c = Task(name="task-c", template="dummy")

    task_c.depends = task_a | task_b

    assert task_c.depends == "(task-a || task-b)"


def test_override_task_next_success_only():
    task_a = Task(name="task-a", template="dummy")
    task_b = Task(name="task-b", template="dummy")

    with Task.set_next_defaults(on=TaskResult.succeeded):
        task_a >> task_b

    assert task_b.depends == "task-a.Succeeded"


def test_override_task_next_success_or_skipped():
    task_a = Task(name="task-a", template="dummy")
    task_b = Task(name="task-b", template="dummy")

    with Task.set_next_defaults(on=TaskResult.succeeded | TaskResult.skipped):
        task_a >> task_b

    assert task_b.depends == "(task-a.Succeeded || task-a.Skipped)"


def test_override_task_next_success_or_skipped_or_daemoned():
    task_a = Task(name="task-a", template="dummy")
    task_b = Task(name="task-b", template="dummy")

    with Task.set_next_defaults(on=TaskResult.succeeded | TaskResult.skipped | TaskResult.daemoned):
        task_a >> task_b

    assert task_b.depends == "(task-a.Succeeded || task-a.Skipped || task-a.Daemoned)"


def test_override_task_next_success_or_skipped_list():
    task_a = Task(name="task-a", template="dummy")
    task_b = Task(name="task-b", template="dummy")

    with Task.set_next_defaults(on=[TaskResult.succeeded, TaskResult.skipped]):
        task_a >> task_b

    assert task_b.depends == "(task-a.Succeeded || task-a.Skipped)"


def test_override_task_next_ignore_duplicate_task_results():
    task_a = Task(name="task-a", template="dummy")
    task_b = Task(name="task-b", template="dummy")

    with Task.set_next_defaults(on=TaskResult.succeeded | TaskResult.succeeded):
        task_a >> task_b

    assert task_b.depends == "task-a.Succeeded"


def test_override_task_next_ignore_duplicate_task_results_list():
    task_a = Task(name="task-a", template="dummy")
    task_b = Task(name="task-b", template="dummy")

    with Task.set_next_defaults(on=[TaskResult.succeeded, TaskResult.succeeded]):
        task_a >> task_b

    assert task_b.depends == "task-a.Succeeded"


def test_override_task_next_ignore_multiple_duplicate_task_results():
    task_a = Task(name="task-a", template="dummy")
    task_b = Task(name="task-b", template="dummy")

    with Task.set_next_defaults(
        on=TaskResult.succeeded | TaskResult.skipped | TaskResult.succeeded | TaskResult.skipped
    ):
        task_a >> task_b

    assert task_b.depends == "(task-a.Succeeded || task-a.Skipped)"


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


def test_override_task_next_on_success_or_skipped_list():
    task_a = Task(name="task-a", template="dummy")
    task_b = Task(name="task-b", template="dummy")
    task_c = Task(name="task-c", template="dummy")

    with Task.set_next_defaults(on=[TaskResult.succeeded, TaskResult.skipped]):
        [task_a, task_b] >> task_c

    assert task_c.depends == "(task-a.Succeeded || task-a.Skipped) && (task-b.Succeeded || task-b.Skipped)"


def test_override_task_next_on_success_or_skipped_or_operator():
    task_a = Task(name="task-a", template="dummy")
    task_b = Task(name="task-b", template="dummy")
    task_c = Task(name="task-c", template="dummy")

    with Task.set_next_defaults(on=TaskResult.succeeded | TaskResult.skipped):
        [task_a, task_b] >> task_c

    assert task_c.depends == "(task-a.Succeeded || task-a.Skipped) && (task-b.Succeeded || task-b.Skipped)"


def test_override_task_next_or_operator_and_on_success_or_skipped():
    task_a = Task(name="task-a", template="dummy")
    task_b = Task(name="task-b", template="dummy")
    task_c = Task(name="task-c", template="dummy")

    with Task.set_next_defaults(operator=Operator.or_, on=TaskResult.succeeded | TaskResult.skipped):
        [task_a, task_b] >> task_c

    assert task_c.depends == "(task-a.Succeeded || task-a.Skipped) || (task-b.Succeeded || task-b.Skipped)"
