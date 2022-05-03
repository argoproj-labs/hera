from hera.task_template import TaskTemplate
from test_task import task_security_context_kwargs  # noqa
import inspect
import test_task


def create_task_from_templated_task(*args, **kwargs):
    return TaskTemplate(*args, **kwargs).task()


# Get all imports from test_task.py and import here.
with open("tests/test_task.py", "r") as file:
    imports = [
        line
        for line in file.readlines()
        if line.startswith("from ") or line.startswith("import ")
    ]
    for i in imports:
        exec(i)


# Get all test names defined in test_task.py.
_test_func_names = [test for test in test_task.__dir__() if test.startswith("test")]

# Modify all tests to use TaskTemplate.
for test_name in _test_func_names:
    f = test_task.__getattribute__(test_name)
    lines = inspect.getsource(f)
    modified_lines = lines.replace("Task(", "TaskTemplate(")
    exec(modified_lines)

# Modify all tests to use TaskTemplate(...).task.
for test_name in _test_func_names:
    f = test_task.__getattribute__(test_name)
    lines = inspect.getsource(f)
    lines = lines.splitlines()

    for index, line in enumerate(lines):
        # Not always first line because of @pytest decorators.
        if line.startswith("def"):
            def_line = line.replace("test_", "test_templated_")
            lines[index] = def_line
            print(def_line)

    lines = "\n".join(lines)
    lines = lines.replace("Task(", "create_task_from_templated_task(")
    exec(lines)


# TODO: test task with all possible tasks: python func, bash func, container, daemon, else...?
