import inspect
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
