import importlib
import logging
import re
from typing import cast

import pytest

import hera.workflows.models as m
from hera.workflows import DAG, Workflow
from hera.workflows.io.v1 import Input
from hera.workflows.models import (
    Artifact as ModelArtifact,
    Parameter as ModelParameter,
    Workflow as ModelWorkflow,
)


def test_set_entrypoint():
    w = importlib.import_module("tests.workflow_decorators.set_entrypoint").w

    assert w.entrypoint == "goodbye-world"


def test_multiple_set_entrypoint(caplog):
    with caplog.at_level(logging.WARNING):
        w = importlib.import_module("tests.workflow_decorators.multiple_entrypoints").w

    assert "entrypoint is being reassigned" in caplog.text
    assert w.entrypoint == "hello-world-2"


def test_dag_io_declaration():
    w: Workflow = importlib.import_module("tests.workflow_decorators.dag_io_declaration").w

    model_workflow = cast(ModelWorkflow, w.build())

    assert len(model_workflow.spec.templates) == 1

    dag_template = model_workflow.spec.templates[0]

    assert dag_template.inputs
    assert len(dag_template.inputs.parameters) == 2
    assert dag_template.inputs.parameters == [
        ModelParameter(name="basic_input_parameter"),
        ModelParameter(name="my-input-param"),
    ]
    assert len(dag_template.inputs.artifacts) == 1
    assert dag_template.inputs.artifacts == [ModelArtifact(name="my-input-artifact")]

    assert dag_template.outputs
    assert len(dag_template.outputs.parameters) == 2
    assert dag_template.outputs.parameters == [
        ModelParameter(name="basic_output_parameter"),
        ModelParameter(name="my-output-param"),
    ]
    assert dag_template.outputs.artifacts == [
        ModelArtifact(name="my-output-artifact"),
    ]


def test_dag_task_arguments():
    w: Workflow = importlib.import_module("tests.workflow_decorators.dag_io_hoisting").w

    model_workflow = cast(ModelWorkflow, w.build())

    assert model_workflow.spec.templates is not None
    assert len(model_workflow.spec.templates) == 2

    dag_template = next(filter(lambda t: t.name == "dummy-dag", model_workflow.spec.templates))

    assert dag_template.dag is not None
    assert len(dag_template.dag.tasks) == 1
    task = dag_template.dag.tasks[0]
    assert task.arguments and task.arguments.parameters and task.arguments.artifacts

    assert task.arguments.parameters == [
        ModelParameter(
            name="basic_input_parameter",
            value="{{inputs.parameters.basic_input_parameter}}",
        ),
        ModelParameter(name="my-input-param", value="{{inputs.parameters.my-input-param}}"),
    ]
    assert task.arguments.artifacts == [
        ModelArtifact(name="my-input-artifact", from_="{{inputs.artifacts.my-input-artifact}}"),
    ]


def test_dag_tasks_with_masked_attributes_in_arguments():
    w: Workflow = importlib.import_module("tests.workflow_decorators.dag_io_masked_parameters").w

    model_workflow = cast(ModelWorkflow, w.build())

    assert model_workflow.spec.templates is not None
    assert len(model_workflow.spec.templates) == 2

    dag_template = next(filter(lambda t: t.name == "dummy-dag", model_workflow.spec.templates))

    assert dag_template.dag is not None
    assert len(dag_template.dag.tasks) == 2
    task_a = next(filter(lambda t: t.name == "task-a", dag_template.dag.tasks))
    assert task_a.arguments and task_a.arguments.parameters

    assert task_a.arguments.parameters == [
        ModelParameter(
            name="name",
            value="{{inputs.parameters.name}}",
        ),
        ModelParameter(name="hooks", value="{{inputs.parameters.hooks}}"),
        ModelParameter(name="target", value="{{inputs.parameters.target}}"),
    ]

    task_b = next(filter(lambda t: t.name == "task-b", dag_template.dag.tasks))
    assert task_b.arguments and task_b.arguments.parameters

    assert task_b.arguments.parameters == [
        ModelParameter(name="name", value="{{tasks.task-a.outputs.parameters.name}}"),
        ModelParameter(name="hooks", value="{{tasks.task-a.outputs.parameters.hooks}}"),
        ModelParameter(name="target", value="{{inputs.parameters.target}}"),
    ]

    assert dag_template.outputs.parameters == [
        ModelParameter(
            name="name",
            value_from={"parameter": "{{tasks.task-a.outputs.parameters.name}}"},
        ),
        ModelParameter(
            name="hooks",
            value_from={"parameter": "{{tasks.task-b.outputs.parameters.hooks}}"},
        ),
        ModelParameter(
            name="target",
            value_from={"parameter": "{{inputs.parameters.target}}"},
        ),
    ]


def test_dag_task_io_hoisting():
    w: Workflow = importlib.import_module("tests.workflow_decorators.dag_io_hoisting").w

    model_workflow = cast(ModelWorkflow, w.build())

    assert model_workflow.spec.templates is not None
    assert len(model_workflow.spec.templates) == 2

    dag_template = next(filter(lambda t: t.name == "dummy-dag", model_workflow.spec.templates))

    assert dag_template.outputs and dag_template.outputs.parameters and dag_template.outputs.artifacts
    assert dag_template.outputs.parameters
    assert dag_template.outputs.artifacts == [
        ModelArtifact(name="my-output-artifact", from_="{{tasks.a-task.outputs.artifacts.my-output-artifact}}"),
    ]


def test_dag_task_auto_depends():
    """The workflow should contain the dag with correct tasks without having to call `build`."""
    w: Workflow = importlib.import_module("tests.workflow_decorators.dag").w

    assert len(w.templates) == 3

    dag_template: DAG = next(iter([t for t in w.templates if t.name == "worker"]), None)

    assert len(dag_template.tasks) == 4

    setup_task = next(iter([t for t in dag_template.tasks if t.name == "setup-task"]), None)
    assert setup_task.depends is None

    task_a = next(iter([t for t in dag_template.tasks if t.name == "task-a"]), None)
    assert task_a.depends == "setup-task"

    task_b = next(iter([t for t in dag_template.tasks if t.name == "task-b"]), None)
    assert task_b.depends == "setup-task"

    final_task = next(iter([t for t in dag_template.tasks if t.name == "final-task-name"]), None)
    assert final_task.depends == "task-a && task-b"


def test_dag_with_inner_dag():
    w: Workflow = importlib.import_module("tests.workflow_decorators.inner_dag").w

    assert len(w.templates) == 4

    outer_dag_template: DAG = next(iter([t for t in w.templates if t.name == "outer-dag"]), None)

    assert len(outer_dag_template.tasks) == 3

    dag_a = next(iter([t for t in outer_dag_template.tasks if t.name == "sub-dag-a"]), None)
    assert dag_a
    assert dag_a.arguments and dag_a.arguments.parameters == [
        ModelParameter(
            name="value_a",
            value="dag_a",
        ),
        ModelParameter(
            name="value_b",
            value="{{inputs.parameters.value_a}}",
        ),
    ]

    dag_b = next(iter([t for t in outer_dag_template.tasks if t.name == "sub-dag-b"]), None)
    assert dag_b
    assert dag_b.arguments and dag_b.arguments.parameters == [
        ModelParameter(
            name="value_a",
            value="dag_b",
        ),
        ModelParameter(
            name="value_b",
            value="{{inputs.parameters.value_b}}",
        ),
    ]

    dag_c = next(iter([t for t in outer_dag_template.tasks if t.name == "sub-dag-c"]), None)
    assert dag_c
    assert dag_c.arguments and dag_c.arguments.parameters == [
        ModelParameter(
            name="value_a",
            value="{{tasks.sub-dag-a.outputs.parameters.value}}",
        ),
        ModelParameter(
            name="value_b",
            value="{{tasks.sub-dag-b.outputs.parameters.value}}",
        ),
    ]


def test_dag_is_runnable():
    """The dag function should be runnable as Python code."""
    from tests.workflow_decorators.dag import WorkerInput, WorkerOutput, worker

    assert worker(WorkerInput(value_a="hello", value_b="world")) == WorkerOutput(
        value="hello linux world Setting things up"
    )


def test_steps_with_parallel_steps_is_runnable(global_config_fixture):
    """The steps function, even with a parallel context, should be runnable as Python code."""
    global_config_fixture.experimental_features["suppress_parameter_default_error"] = True
    from tests.workflow_decorators.steps import WorkerInput, WorkerOutput, worker

    assert worker(WorkerInput(value_a="hello", value_b="world")) == WorkerOutput(
        value="hello linux42 world Setting things up"
    )


def test_dag_func_no_inputs(global_config_fixture):
    # GIVEN
    global_config_fixture.experimental_features["decorator_syntax"] = True
    w = Workflow()

    @w.dag()
    def no_arg_dag() -> None:
        pass

    # WHEN
    model_workflow = cast(m.Workflow, w.build())

    # THEN
    assert model_workflow.spec.templates and model_workflow.spec.templates[0].inputs is None


def test_dag_func_one_input(global_config_fixture):
    # GIVEN
    global_config_fixture.experimental_features["decorator_syntax"] = True
    w = Workflow()

    class DagInput(Input):
        my_int: int

    @w.dag()
    def one_arg_dag_func(_: DagInput) -> None:
        pass

    # WHEN
    model_workflow = cast(m.Workflow, w.build())

    # THEN
    assert model_workflow.spec.templates and model_workflow.spec.templates[0].inputs == m.Inputs(
        parameters=[m.Parameter(name="my_int")]
    )


def test_dag_func_two_inputs_errors(global_config_fixture):
    # GIVEN
    global_config_fixture.experimental_features["decorator_syntax"] = True
    w = Workflow()

    # WHEN/THEN
    with pytest.raises(
        SyntaxError, match=re.escape("dag decorator must be used with a single `Input` arg, or no args.")
    ):

        @w.dag()
        def two_args_dag_func(_1: int, _2: str) -> None:
            pass


def test_dag_return_must_be_new_output(global_config_fixture):
    global_config_fixture.experimental_features["decorator_syntax"] = True

    # WHEN/THEN
    with pytest.raises(SyntaxError, match=re.escape("Function return must be a new Output object.")):
        importlib.import_module("tests.workflow_decorators.dag_return_task_error").w


def test_dag_return_without_annotation_errors(global_config_fixture):
    global_config_fixture.experimental_features["decorator_syntax"] = True

    # WHEN/THEN
    with pytest.raises(
        SyntaxError,
        match=re.escape(
            "Function returned <class 'tests.workflow_decorators.dag_return_none_error.ExampleOutput'>, "
            "expected None (the function may be missing a return annotation)."
        ),
    ):
        importlib.import_module("tests.workflow_decorators.dag_return_none_error").w


def test_passing_input_as_kwarg_errors(global_config_fixture):
    with pytest.raises(
        SyntaxError,
        match=re.escape(
            "Found Input argument(s) in kwargs: ['concat_input']. Input must be passed as a positional-only argument."
        ),
    ):
        importlib.import_module("tests.workflow_decorators.dag_kwarg_error").w


def test_script_single_non_input_arg_errors(global_config_fixture):
    global_config_fixture.experimental_features["decorator_syntax"] = True
    w = Workflow()

    # WHEN/THEN
    with pytest.raises(
        SyntaxError, match=re.escape("script decorator must be used with a single `Input` arg, or no args.")
    ):

        @w.script()
        def two_args_script_func(_1: int) -> None:
            pass


def test_script_regular_args_errors(global_config_fixture):
    global_config_fixture.experimental_features["decorator_syntax"] = True
    w = Workflow()

    # WHEN/THEN
    with pytest.raises(
        SyntaxError, match=re.escape("script decorator must be used with a single `Input` arg, or no args.")
    ):

        @w.script()
        def two_args_script_func(_1: int, _2: str) -> None:
            pass
