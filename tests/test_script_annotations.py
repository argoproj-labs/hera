"""Test script annotations are built correctly within workflows."""
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
    ["artifactory", "azure", "gcs", "git", "hdfs", "optional", "mode", "mode_recurse", "oss", "raw", "sub_path", "s3"],
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


def test_double_default_throws_a_value_error(global_config_fixture):
    """Test asserting that it is not possible to define default in the annotation and normal Python."""

    # GIVEN
    @script()
    def echo_int(an_int: Annotated[int, Parameter(default=1)] = 2):
        print(an_int)

    global_config_fixture.experimental_features["script_annotations"] = True
    with pytest.raises(ValueError) as e:
        with Workflow(generate_name="test-default-", entrypoint="my-steps") as w:
            with Steps(name="my-steps"):
                echo_int()

        w.to_dict()

    assert "default cannot be set via both the function parameter default and the Parameter's default" in str(e.value)


@pytest.mark.parametrize(
    "function_name,expected_input,expected_output",
    [
        (
            "output_parameter_as_function_parameter",
            {"parameters": [{"name": "a_number"}]},
            {"parameters": [{"name": "successor", "valueFrom": {"path": "/tmp/hera/outputs/parameters/successor"}}]},
        ),
        (
            "output_artifact_as_function_parameter",
            {"parameters": [{"name": "a_number"}]},
            {"artifacts": [{"name": "successor", "path": "/tmp/hera/outputs/artifacts/successor"}]},
        ),
        (
            "output_artifact_and_parameter_as_function_parameters",
            {"parameters": [{"name": "a_number"}]},
            {
                "parameters": [{"name": "successor", "valueFrom": {"path": "/tmp/hera/outputs/parameters/successor"}}],
                "artifacts": [{"name": "successor2", "path": "/tmp/hera/outputs/artifacts/successor2"}],
            },
        ),
        (
            "outputs_in_function_parameters_and_return_signature",
            {"parameters": [{"name": "a_number"}]},
            {
                "parameters": [
                    {"name": "successor", "valueFrom": {"path": "/tmp/hera/outputs/parameters/successor"}},
                    {"name": "successor3", "valueFrom": {"path": "/tmp/hera/outputs/parameters/successor3"}},
                ],
                "artifacts": [
                    {"name": "successor2", "path": "/tmp/hera/outputs/artifacts/successor2"},
                    {"name": "successor4", "path": "/tmp/hera/outputs/artifacts/successor4"},
                ],
            },
        ),
        (
            "output_annotations_unnamed_in_function_parameters",
            {"parameters": [{"name": "a_number"}]},
            {
                "parameters": [{"name": "successor", "valueFrom": {"path": "/tmp/hera/outputs/parameters/successor"}}],
                "artifacts": [{"name": "successor2", "path": "/tmp/hera/outputs/artifacts/successor2"}],
            },
        ),
        (
            "custom_output_directory",
            {"parameters": [{"name": "a_number"}]},
            {
                "parameters": [
                    {"name": "successor", "valueFrom": {"path": "/user/chosen/outputs/parameters/successor"}}
                ],
            },
        ),
    ],
)
def test_script_annotated_outputs(function_name, expected_input, expected_output, global_config_fixture):
    """Test that output annotations work correctly by asserting correct inputs and outputs on the built workflow."""
    # GIVEN
    global_config_fixture.experimental_features["script_annotations"] = True
    # Force a reload of the test module, as the runner performs "importlib.import_module", which
    # may fetch a cached version
    import tests.script_annotations.outputs as module

    importlib.reload(module)
    workflow = importlib.import_module("tests.script_annotations.outputs").w

    # WHEN
    workflow_dict = workflow.to_dict()
    assert workflow == Workflow.from_dict(workflow_dict)
    assert workflow == Workflow.from_yaml(workflow.to_yaml())

    # THEN
    template = next(filter(lambda t: t["name"] == function_name.replace("_", "-"), workflow_dict["spec"]["templates"]))
    assert template["inputs"] == expected_input
    assert template["outputs"] == expected_output


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
