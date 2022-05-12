import inspect
from pathlib import Path

import test_task
from test_task import task_security_context_kwargs  # noqa

from hera.resources import Resources
from hera.task_template import TaskTemplate
from hera.volumes import Volume
from hera.workflow import Workflow

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
    t2 = tmpl.task("t2", [{"a": 2}])

    assert tmpl.name == "tmpl"
    assert t1.name == "t1"
    assert t2.name == "t2"

    for p_tmpl in tmpl.get_parameters():
        assert p_tmpl.name == "a"
        assert p_tmpl.value == "1"

    for t1_p in t1.get_parameters():
        assert t1_p.name == "a"
        assert t1_p.value == "1"

    for t2_p in t2.get_parameters():
        assert t2_p.name == "a"
        assert t2_p.value == "2"


def test_two_templates_one_task(no_op):
    tmpl1 = TaskTemplate("tmpl1", no_op)
    tmpl2 = TaskTemplate("tmpl2", no_op)

    t = tmpl1.task("t1")
    assert t.name == "t1"
    assert t.argo_template.name == "tmpl1"

    t = tmpl2.task("t2")
    assert t.name == "t2"
    assert t.argo_template.name == "tmpl2"


def test_many_templates_many_tasks(op):
    tmpl1 = TaskTemplate("tmpl1", op, [{"a": 123}])
    tmpl2 = TaskTemplate("tmpl2", op, [{"a": 456}])

    t1_1, t1_2, t1_3 = tmpl1.task("t1_1"), tmpl1.task("t1_2"), tmpl1.task("t1_3")
    t2_1, t2_2, t2_3 = tmpl2.task("t2_1"), tmpl2.task("t2_2"), tmpl2.task("t2_3")

    for t1 in [t1_1, t1_2, t1_3]:
        assert t1.argo_template.name == "tmpl1"

        for p in t1.get_parameters():
            assert p.name == "a"
            assert p.value == "123"

    for t2 in [t2_1, t2_2, t2_3]:
        assert t2.argo_template.name == "tmpl2"

        for p in t2.get_parameters():
            assert p.name == "a"
            assert p.value == "456"


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


def test_add_multiple_tasks_from_one_task_template_to_workflow(w: Workflow, no_op):
    tmpl = TaskTemplate(
        "tmpl",
        no_op,
    )
    t1, t2, t3 = tmpl.task("t1"), tmpl.task("t2"), tmpl.task("t3")
    w.add_tasks(t1, t2, t3)

    assert len(w.spec.templates[0].to_dict()["dag"]["tasks"]) == 3
    assert (
        len(w.spec.templates) == 2
    ), "Workflow should have 2 templates: one for task template, other for dag template"


def test_task_template_with_volume(w: Workflow, no_op):
    tmpl = TaskTemplate(
        "tmpl",
        no_op,
        resources=Resources(volumes=[Volume(name="test-volume", mount_path="/mnt/test", size="1Mi")]),
    )
    t1, t2, t3 = tmpl.task("t1"), tmpl.task("t2"), tmpl.task("t3")
    w.add_tasks(t1, t2, t3)

    assert id(t1.resources.volumes) == id(t2.resources.volumes) == id(t3.resources.volumes)
