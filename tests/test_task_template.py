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
        # print(i)
        exec(i)


# Get all tests defined in test_task.py and modify to use TaskTemplate.
_test_func_names = [test for test in test_task.__dir__() if test.startswith("test")]
for test_name in _test_func_names:
    f = test_task.__getattribute__(test_name)
    lines = inspect.getsource(f)
    modified_lines = lines.replace("Task(", "TaskTemplate(")
    exec(modified_lines)
