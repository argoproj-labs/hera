"""Test script annotations are built correctly within workflows."""

import importlib
from typing import Annotated

import pytest

from hera.shared._pydantic import _PYDANTIC_VERSION
from hera.workflows import Workflow, script
from hera.workflows.parameter import Parameter
from hera.workflows.steps import Steps

from .test_examples import _compare_workflows


@pytest.mark.parametrize("module_name", ["combined", "description", "enum"])
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


def test_double_default_throws_a_value_error(global_config_fixture):
    """Test asserting that it is not possible to define default in the annotation and normal Python."""

    # GIVEN
    global_config_fixture.experimental_features["suppress_parameter_default_error"] = True

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


def test_parameter_default_without_suppression_throws_a_value_error(global_config_fixture):
    """Test asserting that it is not possible to define default in the annotation and normal Python."""

    # GIVEN
    global_config_fixture.experimental_features["suppress_parameter_default_error"] = False

    @script()
    def echo_int(an_int: Annotated[int, Parameter(default=1)]):
        print(an_int)

    global_config_fixture.experimental_features["script_annotations"] = True
    with pytest.raises(ValueError) as e:
        with Workflow(generate_name="test-default-", entrypoint="my-steps") as w:
            with Steps(name="my-steps"):
                echo_int()

        w.to_dict()

    assert (
        "default cannot be set via the Parameter's default, use a Python default value instead"
        "You can suppress this error by setting "
        'global_config.experimental_features["suppress_parameter_default_error"] = True'
    ) in str(e.value)


@pytest.mark.parametrize(
    "function_name,expected_input,expected_output",
    [
        (
            "output_parameter_as_function_parameter",
            {"parameters": [{"name": "a_number"}]},
            {"parameters": [{"name": "successor", "valueFrom": {"path": "/tmp/hera-outputs/parameters/successor"}}]},
        ),
        (
            "output_artifact_as_function_parameter",
            {"parameters": [{"name": "a_number"}]},
            {"artifacts": [{"name": "successor", "path": "/tmp/hera-outputs/artifacts/successor"}]},
        ),
        (
            "output_artifact_and_parameter_as_function_parameters",
            {"parameters": [{"name": "a_number"}]},
            {
                "parameters": [{"name": "successor", "valueFrom": {"path": "/tmp/hera-outputs/parameters/successor"}}],
                "artifacts": [{"name": "successor2", "path": "/tmp/hera-outputs/artifacts/successor2"}],
            },
        ),
        (
            "outputs_in_function_parameters_and_return_signature",
            {"parameters": [{"name": "a_number"}]},
            {
                "parameters": [
                    {"name": "successor", "valueFrom": {"path": "/tmp/hera-outputs/parameters/successor"}},
                    {"name": "successor3", "valueFrom": {"path": "/tmp/hera-outputs/parameters/successor3"}},
                ],
                "artifacts": [
                    {"name": "successor2", "path": "/tmp/hera-outputs/artifacts/successor2"},
                    {"name": "successor4", "path": "/tmp/hera-outputs/artifacts/successor4"},
                ],
            },
        ),
        (
            "output_annotations_unnamed_in_function_parameters",
            {"parameters": [{"name": "a_number"}]},
            {
                "parameters": [{"name": "successor", "valueFrom": {"path": "/tmp/hera-outputs/parameters/successor"}}],
                "artifacts": [{"name": "successor2", "path": "/tmp/hera-outputs/artifacts/successor2"}],
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
    workflow = importlib.import_module(module.__name__).w

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


@pytest.mark.parametrize(
    "pydantic_mode",
    [
        1,
        _PYDANTIC_VERSION,
    ],
)
@pytest.mark.parametrize(
    "function_name,expected_input,expected_output",
    [
        pytest.param(
            "pydantic_io_params",
            {
                "parameters": [
                    {"name": "my_int", "default": "1"},
                    {"name": "another-int", "default": "42", "description": "my desc"},
                    {"name": "no_default_param"},
                ]
            },
            {
                "parameters": [
                    {"name": "my_output_str", "valueFrom": {"path": "/tmp/hera-outputs/parameters/my_output_str"}},
                    {"name": "second-output", "valueFrom": {"path": "/tmp/hera-outputs/parameters/second-output"}},
                ],
            },
            id="param-only-io",
        ),
        pytest.param(
            "pydantic_io_artifacts",
            {
                "artifacts": [
                    {"name": "file-artifact", "path": "/tmp/hera-inputs/artifacts/file-artifact"},
                    {"name": "an-int-artifact", "path": "/tmp/hera-inputs/artifacts/an-int-artifact"},
                ]
            },
            {
                "artifacts": [
                    {"name": "artifact-output", "path": "/tmp/hera-outputs/artifacts/artifact-output"},
                ],
            },
            id="artifact-only-io",
        ),
        pytest.param(
            "pydantic_io",
            {
                "parameters": [
                    {"name": "param-int", "default": "42"},
                ],
                "artifacts": [
                    {"name": "artifact-int", "path": "/tmp/hera-inputs/artifacts/artifact-int"},
                ],
            },
            {
                "parameters": [
                    {"name": "param-int", "valueFrom": {"path": "/tmp/hera-outputs/parameters/param-int"}},
                ],
                "artifacts": [
                    {"name": "artifact-int", "path": "/tmp/hera-outputs/artifacts/artifact-int"},
                ],
            },
            id="artifact-and-parameter-io",
        ),
        pytest.param(
            "pydantic_io_with_defaults",
            {
                "parameters": [
                    {"name": "my_int", "default": "2"},
                    {"name": "another-int", "default": "24", "description": "my desc"},
                    {"name": "no_default_param", "default": "1"},
                ],
            },
            {
                "parameters": [
                    {"name": "my_output_str", "valueFrom": {"path": "/tmp/hera-outputs/parameters/my_output_str"}},
                    {"name": "second-output", "valueFrom": {"path": "/tmp/hera-outputs/parameters/second-output"}},
                ],
            },
            id="runnerinput-change-default",
        ),
        pytest.param(
            "pydantic_io_within_generic",
            {
                "parameters": [
                    {
                        "name": "my_inputs",
                        "default": '[{"my_int": 1, "my_annotated_int": 42, "no_default_param": 1}, {"my_int": 2, "my_annotated_int": 42, "no_default_param": 2}]',
                    },
                ],
            },
            {
                "parameters": [
                    {"name": "my_output_str", "valueFrom": {"path": "/tmp/hera-outputs/parameters/my_output_str"}},
                    {"name": "second-output", "valueFrom": {"path": "/tmp/hera-outputs/parameters/second-output"}},
                ],
            },
            id="runnerinput-within-generic",
        ),
    ],
)
def test_script_pydantic_io(pydantic_mode, function_name, expected_input, expected_output, global_config_fixture):
    """Test that output annotations work correctly by asserting correct inputs and outputs on the built workflow."""
    # GIVEN
    global_config_fixture.experimental_features["script_annotations"] = True
    global_config_fixture.experimental_features["script_pydantic_io"] = True
    # Force a reload of the test module, as the runner performs "importlib.import_module", which
    # may fetch a cached version
    module_name = f"tests.script_annotations.pydantic_io_v{pydantic_mode}"

    module = importlib.import_module(module_name)
    importlib.reload(module)
    workflow = importlib.import_module(module.__name__).w

    # WHEN
    workflow_dict = workflow.to_dict()
    assert workflow == Workflow.from_dict(workflow_dict)
    assert workflow == Workflow.from_yaml(workflow.to_yaml())

    # THEN
    template = next(filter(lambda t: t["name"] == function_name.replace("_", "-"), workflow_dict["spec"]["templates"]))
    assert template["inputs"] == expected_input
    assert template["outputs"] == expected_output


@pytest.mark.parametrize(
    "pydantic_mode",
    [
        1,
        _PYDANTIC_VERSION,
    ],
)
@pytest.mark.parametrize(
    "function_name,expected_input,expected_output",
    [
        pytest.param(
            "pydantic_io_params",
            {
                "parameters": [
                    {"name": "my_str"},
                    {"name": "my_empty_default_str", "default": ""},
                    {"name": "alt-name", "default": "hello world!"},
                ]
            },
            {
                "parameters": [
                    {"name": "my_output_str", "valueFrom": {"path": "/tmp/hera-outputs/parameters/my_output_str"}},
                    {"name": "second-output", "valueFrom": {"path": "/tmp/hera-outputs/parameters/second-output"}},
                ],
            },
            id="param-only-io",
        ),
    ],
)
def test_script_pydantic_io_strs(pydantic_mode, function_name, expected_input, expected_output, global_config_fixture):
    """Test that output annotations work correctly by asserting correct inputs and outputs on the built workflow."""
    # GIVEN
    global_config_fixture.experimental_features["script_annotations"] = True
    global_config_fixture.experimental_features["script_pydantic_io"] = True
    # Force a reload of the test module, as the runner performs "importlib.import_module", which
    # may fetch a cached version
    module_name = f"tests.script_annotations.pydantic_io_v{pydantic_mode}_strs"

    module = importlib.import_module(module_name)
    importlib.reload(module)
    workflow = importlib.import_module(module.__name__).w

    # WHEN
    workflow_dict = workflow.to_dict()
    assert workflow == Workflow.from_dict(workflow_dict)
    assert workflow == Workflow.from_yaml(workflow.to_yaml())

    # THEN
    template = next(filter(lambda t: t["name"] == function_name.replace("_", "-"), workflow_dict["spec"]["templates"]))
    assert template["inputs"] == expected_input
    assert template["outputs"] == expected_output


def test_script_pydantic_invalid_outputs(global_config_fixture):
    """Test that output annotations work correctly by asserting correct inputs and outputs on the built workflow."""
    # GIVEN
    global_config_fixture.experimental_features["script_annotations"] = True
    global_config_fixture.experimental_features["script_pydantic_io"] = True
    # Force a reload of the test module, as the runner performs "importlib.import_module", which
    # may fetch a cached version
    import tests.script_annotations.pydantic_io_invalid_outputs as module

    importlib.reload(module)
    workflow = importlib.import_module(module.__name__).w

    # WHEN / THEN
    with pytest.raises(ValueError) as e:
        workflow.to_dict()

    assert "Output cannot be part of a tuple output" in str(e.value)


def test_script_pydantic_multiple_inputs(global_config_fixture):
    """Test that parameters with same annotated name raises ValueError."""
    # GIVEN
    global_config_fixture.experimental_features["script_annotations"] = True
    global_config_fixture.experimental_features["script_pydantic_io"] = True
    # Force a reload of the test module, as the runner performs "importlib.import_module", which
    # may fetch a cached version
    import tests.script_annotations.pydantic_io_invalid_multiple_inputs as module

    importlib.reload(module)
    workflow = importlib.import_module(module.__name__).w

    # WHEN / THEN
    with pytest.raises(SyntaxError) as e:
        workflow.to_dict()

    assert "Only one function parameter can be specified when using an Input" in str(e.value)


def test_script_pydantic_without_experimental_flag(global_config_fixture):
    """Test that artifacts with same annotated name raises ValueError."""
    # GIVEN
    global_config_fixture.experimental_features["script_annotations"] = True
    global_config_fixture.experimental_features["script_pydantic_io"] = False
    # Force a reload of the test module, as the runner performs "importlib.import_module", which
    # may fetch a cached version
    import tests.script_annotations.pydantic_io_v1 as module

    importlib.reload(module)
    workflow = importlib.import_module(module.__name__).w

    # WHEN / THEN
    with pytest.raises(ValueError) as e:
        workflow.to_dict()

    assert (
        "Unable to instantiate <class 'tests.script_annotations.pydantic_io_v1.ParamOnlyInput'> since it is an experimental feature."
        in str(e.value)
    )


@pytest.mark.parametrize(
    "module_name",
    [
        "tests.script_annotations.with_param",  # annotated types
        "tests.script_annotations.pydantic_io_with_param",  # Pydantic IO types
    ],
)
def test_script_with_param(global_config_fixture, module_name):
    """Test that with_param works correctly with annotated/Pydantic IO types."""
    # GIVEN
    global_config_fixture.experimental_features["script_annotations"] = True
    global_config_fixture.experimental_features["script_pydantic_io"] = True
    # Force a reload of the test module, as the runner performs "importlib.import_module", which
    # may fetch a cached version

    module = importlib.import_module(module_name)
    importlib.reload(module)
    workflow = importlib.import_module(module.__name__).w

    # WHEN
    workflow_dict = workflow.to_dict()
    assert workflow == Workflow.from_dict(workflow_dict)
    assert workflow == Workflow.from_yaml(workflow.to_yaml())

    # THEN
    (dag,) = (t for t in workflow_dict["spec"]["templates"] if t["name"] == "dag")
    (consume_task,) = (t for t in dag["dag"]["tasks"] if t["name"] == "consume")

    assert consume_task["arguments"]["parameters"] == [
        {
            "name": "some-value",
            "value": "{{item}}",
            "description": "this is some value",
        }
    ]
    assert consume_task["withParam"] == "{{tasks.generate.outputs.parameters.some-values}}"


@pytest.mark.parametrize(
    ("module_name", "input_name"),
    [
        pytest.param("tests.script_annotations.literals", "my_str", id="bare-type-annotation"),
        pytest.param("tests.script_annotations.annotated_literals", "my-str", id="annotated"),
        pytest.param("tests.script_annotations.pydantic_io_literals", "my_str", id="pydantic-io"),
    ],
)
def test_script_literals(global_config_fixture, module_name, input_name):
    """Test that Literals work correctly as direct type annotations."""
    # GIVEN
    global_config_fixture.experimental_features["script_annotations"] = True

    # Force a reload of the test module, as the runner performs "importlib.import_module", which
    # may fetch a cached version
    module = importlib.import_module(module_name)
    importlib.reload(module)
    workflow: Workflow = importlib.import_module(module.__name__).w

    # WHEN
    workflow_dict = workflow.to_dict()
    assert workflow == Workflow.from_dict(workflow_dict)
    assert workflow == Workflow.from_yaml(workflow.to_yaml())

    # THEN
    (literal_str,) = (t for t in workflow_dict["spec"]["templates"] if t["name"] == "literal-str")

    assert literal_str["inputs"]["parameters"] == [{"name": input_name, "enum": ["foo", "bar"]}]
