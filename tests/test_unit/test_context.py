import pytest

from hera.workflows import DAG, Step, Steps, WorkflowTemplate, script
from hera.workflows.container import Container
from hera.workflows.exceptions import InvalidType, NodeNameConflict
from hera.workflows.steps import Parallel
from hera.workflows.task import Task
from hera.workflows.workflow import Workflow


class TestContextNameConflicts:
    """These tests ensure that template and node name conflicts raise Exceptions.
    This should validate that no two templates have the same name,
    and that no two Task/Step nodes have the same name.
    """

    def test_allows_recursive_steps(self):
        """Recursive steps should not cause an error.

        See https://github.com/argoproj-labs/hera/issues/1151
        """

        @script(constructor="inline")
        def random_roll():
            import random

            return random.randint(0, 2)

        with WorkflowTemplate(name="my-workflow", entrypoint="steps"):
            with Steps(name="sub-steps") as st:
                random_number = random_roll()
                Step(
                    name="recurse",
                    arguments={"input-num": random_number.result},
                    template=st,
                    when=f"{random_number.result} != 0",
                )

            with Steps(name="steps"):
                st()

    def test_no_conflict_on_tasks_with_different_names_using_same_template(self):
        """Task nodes can have different names for the same script template."""
        dag_name = "dag-name"
        name_1 = "task-1"
        name_2 = "task-2"

        @script()
        def example():
            print("hello")

        with WorkflowTemplate(
            name="my-workflow",
            entrypoint=dag_name,
        ), DAG(name=dag_name):
            example(name=name_1)
            example(name=name_2)

    def test_no_conflict_on_dag_and_task_with_same_name(self):
        """Dag and task node can have the same name."""
        name = "name-of-dag-and-task"

        @script()
        def example():
            print("hello")

        with WorkflowTemplate(
            name="my-workflow",
            entrypoint=name,
        ), DAG(name=name):
            example(name=name)  # task name same as dag template

        with WorkflowTemplate(
            name="my-workflow",
            entrypoint=name,
        ), Steps(name=name):
            example(name=name)  # step name same as steps template

    def test_conflict_on_multiple_tasks_with_same_name(self):
        """Dags cannot have two task nodes with the same name."""
        name = "name-of-tasks"

        @script()
        def hello():
            print("hello")

        @script()
        def world():
            print("world")

        with pytest.raises(NodeNameConflict):
            with WorkflowTemplate(name="my-workflow", entrypoint="dag"), DAG(name="dag"):
                hello(name=name)
                world(name=name)

        with pytest.raises(NodeNameConflict):
            with WorkflowTemplate(name="my-workflow", entrypoint="steps"), Steps(name="steps"):
                hello(name=name)
                world(name=name)

        with pytest.raises(NodeNameConflict):
            with WorkflowTemplate(
                name="my-workflow",
                entrypoint="steps",
            ), Steps(name="steps") as s:
                hello(name=name)
                with s.parallel():
                    world(name=name)

        with pytest.raises(NodeNameConflict):
            with WorkflowTemplate(
                name="my-workflow",
                entrypoint="steps",
            ), Steps(name="steps") as s:
                with s.parallel():
                    hello(name=name)
                    world(name=name)

        with pytest.raises(NodeNameConflict):
            with WorkflowTemplate(
                name="my-workflow",
                entrypoint="steps",
            ), Steps(name="steps") as s:
                with s.parallel():
                    hello(name=name)
                with s.parallel():
                    world(name=name)


def test_error_outside_of_workflow_context():
    @script()
    def hello():
        print("hello")

    with pytest.raises(SyntaxError, match="Not under a Workflow context"):
        with Steps(name="test"):
            hello()


def test_error_outside_of_workflow_context_decorator_flag(global_config_fixture):
    global_config_fixture.experimental_features["decorator_syntax"] = True

    @script()
    def hello():
        print("hello")

    with pytest.raises(SyntaxError, match="Not under a TemplateSet/Workflow context"):
        with Steps(name="test"):
            hello()


def test_initialise_container_within_steps_context_is_allowed():
    # The Container created under the `Steps` context will be grabbed by `Steps._add_sub`,
    # which will add it to the Workflow templates. The `Step` itself will be added by `Steps._add_sub`, so
    # the Container will be added as a template in the Workflow
    with Workflow(generate_name="test-") as w:
        with Steps(name="test"):
            Step(name="test-step", template=Container())

    assert len(w.templates) == 2
    assert isinstance(w.templates[0], Steps)
    assert isinstance(w.templates[1], Container)


def test_initialise_container_not_referenced_directly_within_steps_context_is_allowed():
    # This test covers an edge case where the Step references the container template
    # by name, not the through the object itself. The Workflow should still have the container
    # as a template, and the `Steps` template should only have 1 sub-step.
    with Workflow(generate_name="test-") as w:
        with Steps(name="test"):
            Container(name="container")
            Step(name="step", template="container")

    assert len(w.templates) == 2
    assert isinstance(w.templates[0], Steps)
    assert len(w.templates[0].sub_steps) == 1

    assert isinstance(w.templates[1], Container)


def test_initialise_container_within_parallel_steps_context_is_allowed():
    # The Container created under the `Steps` context will be grabbed by `Steps._add_sub`,
    # which will add it to the Workflow templates. The `Step` itself will be added by `Steps._add_sub`, so
    # the Container will be added as a template in the Workflow
    with Workflow(generate_name="test-") as w:
        with Steps(name="test") as s:
            with s.parallel():
                Step(name="test-step", template=Container())

    assert len(w.templates) == 2
    assert isinstance(w.templates[0], Steps)
    assert isinstance(w.templates[0].sub_steps[0], Parallel)
    assert isinstance(w.templates[1], Container)


def test_initialise_container_not_referenced_directly_within_parallel_steps_context_is_allowed():
    # This test covers an edge case where the Step references the container template
    # by name, not the through the object itself. The Workflow should still have the container
    # as a template, and the `Steps` template should only have 1 sub-step.
    with Workflow(generate_name="test-") as w:
        with Steps(name="test") as s:
            with s.parallel():
                Container(name="container")
                Step(name="step", template="container")

    assert len(w.templates) == 2
    assert isinstance(w.templates[0], Steps)
    assert isinstance(w.templates[0].sub_steps[0], Parallel)
    assert len(w.templates[0].sub_steps[0].sub_steps) == 1

    assert isinstance(w.templates[1], Container)


def test_initialise_container_within_dag_context_is_allowed():
    # The Container created under the `DAG` context will be grabbed by `DAG._add_sub`,
    # which will add it to the Workflow templates. The `Task` itself will be added by `DAG._add_sub`, so
    # the Container will be added as a template in the Workflow
    with Workflow(generate_name="test-") as w:
        with DAG(name="test"):
            Task(name="task", template=Container())

    assert len(w.templates) == 2
    assert isinstance(w.templates[0], DAG)
    assert isinstance(w.templates[1], Container)


def test_initialise_container_not_referenced_directly_within_dag_context_is_allowed():
    # This test covers an edge case where the Task references the container template
    # by name, not the through the object itself. The Workflow should still have the container
    # as a template, and the `DAG` template should only have 1 sub-step.
    with Workflow(generate_name="test-") as w:
        with DAG(name="test"):
            Container(name="container")
            Task(name="task", template="container")

    assert len(w.templates) == 2
    assert isinstance(w.templates[0], DAG)
    assert len(w.templates[0].tasks) == 1

    assert isinstance(w.templates[1], Container)


def test_wrong_subtype_under_dag_context():
    with pytest.raises(InvalidType):
        with Workflow(generate_name="test-"):
            with DAG(name="test"):
                Step(name="step", template=Container(name="container"))


def test_wrong_subtype_under_steps_context():
    with pytest.raises(InvalidType):
        with Workflow(generate_name="test-"):
            with Steps(name="test"):
                Task(name="task", template=Container(name="container"))
