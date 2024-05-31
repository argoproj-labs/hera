import pytest

from hera.workflows import DAG, Steps, WorkflowTemplate, script
from hera.workflows.exceptions import NodeNameConflict, TemplateNameConflict


class TestContextNameConflicts:
    """These tests ensure that template and node name conflicts raise Exceptions.
    This should validate that no two templates have the same name,
    and that no two Task/Step nodes have the same name.
    """

    def test_conflict_on_templates_with_same_name(self):
        """Multiple templates can't have the same name."""
        name = "name-of-dag-and-script"

        @script(name=name)
        def example():
            print("hello")

        with pytest.raises(TemplateNameConflict):
            with WorkflowTemplate(name="my-workflow", entrypoint=name), DAG(name=name):
                example()

        with pytest.raises(TemplateNameConflict):
            with WorkflowTemplate(
                name="my-workflow",
                entrypoint=name,
            ), Steps(name=name):
                example()

    def test_no_conflict_on_tasks_with_different_names_using_same_template(self):
        """Task nodes can have different names for the same script template."""
        name_1 = "task-1"
        name_2 = "task-2"

        @script()
        def example():
            print("hello")

        with WorkflowTemplate(
            name="my-workflow",
            entrypoint=name,
        ), DAG(name=name):
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

    def test_conflict_on_multiple_scripts_with_same_name(self):
        """Dags cannot have two scripts with the same name."""
        name = "name-of-tasks"

        @script(name=name)  # same template name
        def hello():
            print("hello")

        @script(name=name)  # same template name
        def world():
            print("world")

        with pytest.raises(TemplateNameConflict):
            with WorkflowTemplate(
                name="my-workflow",
                entrypoint=name,
            ), DAG(name="dag"):
                hello()
                world()

        with pytest.raises(TemplateNameConflict):
            with WorkflowTemplate(
                name="my-workflow",
                entrypoint=name,
            ), Steps(name="steps"):
                hello()
                world()

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
