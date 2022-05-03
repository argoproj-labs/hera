from hera.task_template import TaskTemplate  # noqa
from test_task import task_security_context_kwargs  # noqa
import inspect
import test_task

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

# Modify all tests to use TaskTemplate(...).task
for test_name in _test_func_names:
    f = test_task.__getattribute__(test_name)
    lines = inspect.getsource(f)

    def_line = next((line for line in lines.splitlines() if line.startswith("def")))
    def_line = def_line.replace("test_", "test_templated_task_")
    # print(def_line)
    lines = lines.splitlines()
    lines[0] = def_line
    print(lines)
    # print(lines)
    break

    # modified_lines = lines.replace("Task(", "TaskTemplate(")
    # exec(modified_lines)
