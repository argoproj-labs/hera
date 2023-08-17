import importlib

import pytest
from test_examples import _compare_workflows

try:
    from typing import Annotated  # type: ignore
except ImportError:
    from typing_extensions import Annotated  # type: ignore

from hera.workflows import Workflow, script
from hera.workflows.parameter import Parameter
from hera.workflows.steps import Steps


@pytest.mark.parametrize("module_name", ["combined", "default", "description", "enum"])
def test_script_annotations_parameter_regression(module_name, global_config_fixture):
    """Regression tests for the input parameter annotations.

    Check if the workflow created using the new syntax is equivalent
    to one created using the old syntax.
    """

    # GIVEN
    global_config_fixture.experimental_features["script_annotations"] = True
    workflow_old = importlib.import_module(
        f"tests.script_annotations_inputs_regression.script_annotations_parameters_{module_name}_old"
    ).w
    workflow_new = importlib.import_module(
        f"tests.script_annotations_inputs_regression.script_annotations_parameters_{module_name}_new"
    ).w

    # WHEN
    output_old = workflow_old.to_dict()
    output_new = workflow_new.to_dict()

    # THEN
    _compare_workflows(workflow_old, output_old, output_new)


@pytest.mark.parametrize(
    "module_name",
    ["artifactory", "azure", "gcs", "git", "hdfs", "optional", "mode", "mode_recurse", "oss", "raw", "subpath", "s3"],
)
def test_script_annotations_artifact_regression(module_name, global_config_fixture):
    """Regression tests for the input artifact annotations.

    Check if the workflow created using the new syntax is equivalent
    to one created using the old syntax.
    """

    # GIVEN
    global_config_fixture.experimental_features["script_annotations"] = True
    workflow_old = importlib.import_module(
        f"tests.script_annotations_inputs_regression.script_annotations_artifacts_{module_name}_old"
    ).w
    workflow_new = importlib.import_module(
        f"tests.script_annotations_inputs_regression.script_annotations_artifacts_{module_name}_new"
    ).w

    # WHEN
    output_old = workflow_old.to_dict()
    output_new = workflow_new.to_dict()

    # THEN
    _compare_workflows(workflow_old, output_old, output_new)


@script()
def echo_int(an_int: Annotated[int, Parameter(default=1)] = 2):
    print(an_int)


def test_double_default_throws_a_value_error(global_config_fixture):
    """Test asserting that it is not possible to define default in the annotation and normal Python."""

    global_config_fixture.experimental_features["script_annotations"] = True
    with pytest.raises(ValueError) as e:
        with Workflow(generate_name="test-default-", entrypoint="my_steps") as w:
            with Steps(name="my_steps"):
                echo_int()

        w.to_dict()

    assert "The default cannot be set via both the function parameter default and the annotation's default" in str(
        e.value
    )


@pytest.mark.parametrize(
    "module,expected_output,expected_input",
    [
        (
            "script_annotations_output_param_in_func",
            {"parameters": [{"name": "successor"}]},
            {"parameters": [{"name": "a_number"}]},
        ),
        (
            "script_annotations_output_artifact_in_func",
            {"artifacts": [{"name": "successor"}]},
            {"parameters": [{"name": "a_number"}]},
        ),
        (
            "script_annotations_output_param_and_artifact_in_func",
            {"parameters": [{"name": "successor"}], "artifacts": [{"name": "successor2"}]},
            {"parameters": [{"name": "a_number"}]},
        ),
        (
            "script_annotations_output_param_and_artifact_mix",
            {
                "parameters": [{"name": "successor"}, {"name": "successor3"}],
                "artifacts": [{"name": "successor2"}, {"name": "successor4"}],
            },
            {"parameters": [{"name": "a_number"}]},
        ),
        (
            "script_annotations_output_in_func_no_name",
            {
                "parameters": [{"name": "successor"}],
                "artifacts": [{"name": "successor2"}],
            },
            {"parameters": [{"name": "a_number"}]},
        ),
    ],
)
def test_script_annotations_outputs(module, expected_output, expected_input, global_config_fixture):
    """Test that output annotations work correctly by asserting correct inputs and outputs."""
    # GIVEN
    global_config_fixture.experimental_features["script_annotations"] = True
    workflow = importlib.import_module(f"tests.script_annotations_outputs.{module}").w

    # WHEN
    assert workflow.to_dict() == Workflow.from_dict(workflow.to_dict()).to_dict()
    assert workflow == Workflow.from_yaml(workflow.to_yaml())

    outputs = workflow.to_dict()["spec"]["templates"][1]["outputs"]
    inputs = workflow.to_dict()["spec"]["templates"][1]["inputs"]

    # THEN
    assert outputs == expected_output
    assert inputs == expected_input


def test_configmap(global_config_fixture):
    # GIVEN
    global_config_fixture.experimental_features["script_annotations"] = True
    workflow_old = importlib.import_module("script_annotations_inputs_regression.script_annotations_configmap_old").w
    workflow_new = importlib.import_module("script_annotations_inputs_regression.script_annotations_configmap_new").w

    # WHEN
    output_old = workflow_old.to_dict()
    output_new = workflow_new.to_dict()

    # THEN
    _compare_workflows(workflow_old, output_old, output_new)
