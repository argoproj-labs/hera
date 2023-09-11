import importlib

import pytest
from .test_examples import _compare_workflows

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
    global_config_fixture.experimental_features["script_annotations"] = False
    workflow_old = importlib.import_module(
        f"tests.script_annotations_inputs_regression.script_annotations_parameters_{module_name}_old"
    ).w
    output_old = workflow_old.to_dict()

    global_config_fixture.experimental_features["script_annotations"] = True
    workflow_new = importlib.import_module(
        f"tests.script_annotations_inputs_regression.script_annotations_parameters_{module_name}_new"
    ).w
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
    global_config_fixture.experimental_features["script_annotations"] = False
    workflow_old = importlib.import_module(
        f"tests.script_annotations_inputs_regression.script_annotations_artifacts_{module_name}_old"
    ).w
    output_old = workflow_old.to_dict()

    global_config_fixture.experimental_features["script_annotations"] = True
    workflow_new = importlib.import_module(
        f"tests.script_annotations_inputs_regression.script_annotations_artifacts_{module_name}_new"
    ).w
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
        with Workflow(generate_name="test-default-", entrypoint="my-steps") as w:
            with Steps(name="my-steps"):
                echo_int()

        w.to_dict()

    assert "default cannot be set via both the function parameter default and the Parameter's default" in str(e.value)


@pytest.mark.parametrize(
    "module,expected_input,expected_output",
    [
        (
            "script_annotations_output_param_in_func",
            {"parameters": [{"name": "a_number"}]},
            {"parameters": [{"name": "successor", "valueFrom": {"path": "/hera/outputs/parameters/successor"}}]},
        ),
        (
            "script_annotations_output_artifact_in_func",
            {"parameters": [{"name": "a_number"}]},
            {"artifacts": [{"name": "successor", "path": "/hera/outputs/artifacts/successor"}]},
        ),
        (
            "script_annotations_output_param_and_artifact_in_func",
            {"parameters": [{"name": "a_number"}]},
            {
                "parameters": [{"name": "successor", "valueFrom": {"path": "/hera/outputs/parameters/successor"}}],
                "artifacts": [{"name": "successor2", "path": "/hera/outputs/artifacts/successor2"}],
            },
        ),
        (
            "script_annotations_output_param_and_artifact_mix",
            {"parameters": [{"name": "a_number"}]},
            {
                "parameters": [
                    {"name": "successor", "valueFrom": {"path": "/hera/outputs/parameters/successor"}},
                    {"name": "successor3", "valueFrom": {"path": "/hera/outputs/parameters/successor3"}},
                ],
                "artifacts": [
                    {"name": "successor2", "path": "/hera/outputs/artifacts/successor2"},
                    {"name": "successor4", "path": "/hera/outputs/artifacts/successor4"},
                ],
            },
        ),
        (
            "script_annotations_output_in_func_no_name",
            {"parameters": [{"name": "a_number"}]},
            {
                "parameters": [{"name": "successor", "valueFrom": {"path": "/hera/outputs/parameters/successor"}}],
                "artifacts": [{"name": "successor2", "path": "/hera/outputs/artifacts/successor2"}],
            },
        ),
        (
            "script_annotations_output_custom_output_directory",
            {"parameters": [{"name": "a_number"}]},
            {
                "parameters": [
                    {"name": "successor", "valueFrom": {"path": "/user/chosen/outputs/parameters/successor"}}
                ],
            },
        ),
    ],
)
def test_script_annotations_outputs(module, expected_input, expected_output, global_config_fixture):
    """Test that output annotations work correctly by asserting correct inputs and outputs."""
    # GIVEN
    global_config_fixture.experimental_features["script_annotations"] = True
    workflow = importlib.import_module(f"tests.script_annotations_outputs.{module}").w

    # WHEN
    workflow_dict = workflow.to_dict()
    assert workflow == Workflow.from_dict(workflow_dict)
    assert workflow == Workflow.from_yaml(workflow.to_yaml())

    inputs = workflow_dict["spec"]["templates"][1]["inputs"]
    outputs = workflow_dict["spec"]["templates"][1]["outputs"]

    # THEN
    assert inputs == expected_input
    assert outputs == expected_output


def test_configmap(global_config_fixture):
    # GIVEN
    global_config_fixture.experimental_features["script_annotations"] = False
    workflow_old = importlib.import_module(
        "tests.script_annotations_inputs_regression.script_annotations_configmap_old"
    ).w
    output_old = workflow_old.to_dict()

    global_config_fixture.experimental_features["script_annotations"] = True
    workflow_new = importlib.import_module(
        "tests.script_annotations_inputs_regression.script_annotations_configmap_new"
    ).w
    output_new = workflow_new.to_dict()

    # THEN
    _compare_workflows(workflow_old, output_old, output_new)
