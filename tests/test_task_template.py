import inspect
from os import TMP_MAX
from pathlib import Path

import test_task
from test_task import task_security_context_kwargs  # noqa

from hera.task_template import TaskTemplate

# Get test_task.py path into Path.
test_task_file = Path(__file__).parent.joinpath("test_task.py")

# Get all test names defined in test_task.py.
_test_func_names = [test for test in test_task.__dir__() if test.startswith("test")]


def create_task_from_templated_task(*args, **kwargs):
    """
    Use this function to modify imported tests from test_task.py to use task
    generated from task template.
    """
    return TaskTemplate(*args, **kwargs).task()


# Get all imports from test_task.py and import here.
with open(test_task_file, "r") as file:
    imports = [line for line in file.readlines() if line.startswith("from ") or line.startswith("import ")]
    for i in imports:
        exec(i)


# Modify all tests to use TaskTemplate. Execution of Task(...) and
# TaskTemplate(...) should be the same since TaskTemplate inherits from Task.
for test_name in _test_func_names:
    _test_func = test_task.__getattribute__(test_name)
    source = inspect.getsource(_test_func)
    modified_source = source.replace("Task(", "TaskTemplate(")
    exec(modified_source)


# Modify all tests to use TaskTemplate(...).task. And change test names to avoid
# duplicates.
for test_name in _test_func_names:
    _test_func = test_task.__getattribute__(test_name)
    source = inspect.getsource(_test_func)
    lines = source.splitlines()

    for index, line in enumerate(lines):
        # Not always first line because of @pytest decorators.
        if line.startswith("def"):
            def_line = line.replace("test_", "test_templated_")
            lines[index] = def_line

    modified_source = "\n".join(lines)
    modified_source = modified_source.replace("Task(", f"{create_task_from_templated_task.__name__}(")
    exec(modified_source)


def test_one_template_two_tasks(op):
    tmpl = TaskTemplate("tmpl", op, [{"a": 1}])

    t1 = tmpl.task("t1")
    t2 = tmpl.task("t2", [{"a": 3}])

    assert tmpl.name == "tmpl", "TaskTemplate name mismatch"
    assert t1.name == "t1", "t1 name mismatch"
    assert t2.name == "t2", "t2 name mismatch"

    for p_tmpl in tmpl.get_parameters():
        assert p_tmpl.name == "a", "TaskTemplate param name mismatch"
        assert p_tmpl.value == "1", "TaskTemplate default param value mismatch"

    for t1_p in t1.get_parameters():
        assert t1_p.name == "a", "t1 param name mismatch"
        assert t1_p.value == "1", "t1 default param value mismatch"

    for t2_p in t2.get_parameters():
        assert t2_p.name == "a", "t2 param name mismatch"
        assert t2_p.value == "3", "t2 param value mismatch"


def test_two_templates_one_task():
    ...


def test_many_templates_many_tasks():
    ...


def test_template_with_multiple_args(op):
    tmpl = TaskTemplate("tmpl", op, [{"a": 1}, {"a": 2}])

    t1 = tmpl.task("t1")
    t2 = tmpl.task("t2", [{"a": 3}, {"a": 4}])

    for t1_p in t1.get_parameters():
        assert t1_p.name == "a"
        assert t1_p.value == "{{item.a}}"

    for t2_p in t2.get_parameters():
        assert t2_p.name == "a"
        assert t2_p.value == "{{item.a}}"

    t1_items = t1.get_task_spec().with_items
    t2_items = t2.get_task_spec().with_items

    assert t1_items[0].value["a"] == "1"
    assert t1_items[1].value["a"] == "2"

    assert t2_items[0].value["a"] == "3"
    assert t2_items[1].value["a"] == "4"
