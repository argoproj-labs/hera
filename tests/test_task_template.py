from hera.task_template import TaskTemplate  # noqa
from test_task import task_security_context_kwargs  # noqa
import inspect
import test_task


def create_task_from_templated_task(*args, **kwargs):
    args_str = ', '.join(map(str,args))
    kwargs_str = ','.join('{}={}'.format(k,v) for k,v in kwargs.items())
    print(f"{args_str=}")
    print(f"{kwargs_str=}")
    # task = TaskTemplate(*args, **kwargs).task(name="asd")
    task = TaskTemplate(*args, **kwargs).task()
    return task


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

# ############################# #
# comment out for testing start #
# ############################# #
# Modify all tests to use TaskTemplate(...).task
for test_name in _test_func_names:
    f = test_task.__getattribute__(test_name)
    lines = inspect.getsource(f)
    lines = lines.splitlines()

    for index, line in enumerate(lines):
        # either first or second line because of @pytest decorators
        if line.startswith("def"):
            def_line = line.replace("test_", "test_templated_")
            lines[index] = def_line
            print(def_line)

    lines = "\n".join(lines)
    lines = lines.replace("Task(", "create_task_from_templated_task(")
    if test_name == "test_param_getter_parses_single_param_val_on_json_payload":
        print(lines)
    try:
        exec(lines)
    except Exception:
        print(lines)
        break
    # break
# ########################### #
# comment out for testing end #
# ########################### #


# def test_templated_param_getter_parses_single_param_val_on_json_payload(op):
#     t = create_task_from_templated_task('t', op, [{'a': 1}])
#     print(t.get_parameters())
#     param = t.get_parameters()[0]
#     assert param.name == 'a'
#     assert param.value == '1'  # from json.dumps
