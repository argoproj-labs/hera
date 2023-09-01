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


@pytest.mark.parametrize(
    "module_name",
    [
        # "any_success_all_fail", -> with_param
        # "artifact_with_fanout", -> with_param
        "artifact",
        "callable_dag",
        "callable_script",
        "callable_steps",
        "complex_deps",
        "daemon",
        "daemon_nginx",
        "dag_custom_metrics",
        "dag_conditional_parameters",
        "dag_diamond",
        "dag_diamond_with_callable_container",
        "dag_diamond_with_callable_decorators",
        "dag_diamond_with_callable_script",
        "dag_with_script_output_param_passing",
        "dag_with_script_param_passing",
        "dag_nested",
        "dag_targets",
        "dag_task_level_timeout",
        "default_param_overwrite",
        # "dynamic_fanout_container", -> with_param
        # "dynamic_fanout_fanin", -> with_param
        # "dynamic_fanout", -> with_param
        "exit_handler_step_level",
        "loops_dag",
        "loops_maps",
        "loops_param_result",
        "loops",
        "map_reduce",
        "on_exit",
        "output_parameter",
        "parallelism_limit",
        "parallelism_nested",
        "parallelism_nested_dag",
        "parallelism_template_limit",
        "script_annotations",
        "script_annotations_outputs",
        "script_artifact_passing",
        "script_auto_infer",
        # "script_loops_maps", -> with_items
        "script_variations",
        "script_with_default_params",
        "steps_with_callable_container",
        "suspend_template",
        "suspend_template_outputs",
        "template_on_exit",
        "timeouts_workflow",
        "volume_mounts",
        "volume_mounts_wt",
        "volumes_pvc",
        "with_sequence",
        "workflow_event_binding__event_consumer_workflowtemplate",
        "workflow_on_exit",
    ],
)
def test_regression_arguments_passing(module_name, global_config_fixture):
    # GIVEN
    global_config_fixture.experimental_features["script_annotations"] = True
    workflow_old = importlib.import_module(f"tests.arguments_passing_regression.{module_name}_old").w
    workflow_new = importlib.import_module(f"tests.arguments_passing_regression.{module_name}_new").w

    # WHEN
    output_old = workflow_old.to_dict()
    output_new = workflow_new.to_dict()

    # don't care about file names for the runner
    try:
        templates_old = output_old["spec"]["templates"]
        templates_new = output_new["spec"]["templates"]
        for i, t in enumerate(templates_old):
            if "script" in t:
                templates_old[i]["script"]["args"] = templates_new[i]["script"]["args"]
    except KeyError as e:
        print(e)

    # THEN
    _compare_workflows(workflow_old, output_old, output_new)
