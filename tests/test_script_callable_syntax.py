import importlib

import pytest
from tests.test_examples import _compare_workflows


@pytest.mark.parametrize(
    "module_name",
    [
        "any_success_all_fail",  # -> with_param
        "callable_script",
        "callable_steps",
        "complex_deps",
        "daemon",
        "dag_conditional_parameters",
        "dag_diamond_with_callable_decorators",
        "dag_diamond_with_callable_script",
        "dag_with_script_output_param_passing",
        "dag_with_script_param_passing",
        "default_param_overwrite",
        "dynamic_fanout_extra_kwargs",
        "dynamic_fanout_fanin",  # -> with_param
        "dynamic_fanout",  # -> with_param
        "dynamic_fanout_json_payload",
        "on_exit",
        "script_annotations",
        "script_annotations_outputs",
        "script_auto_infer",
        "script_loops_maps",  # -> with_items
        "script_variations",
        "script_with_default_params",
        "suspend_template",
        "template_on_exit",
        "volumes_pvc",
        "with_sequence",
        "workflow_on_exit",
    ],
)
def test_regression_arguments_passing_scripts(module_name):
    # GIVEN
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
    except KeyError:
        pass

    # THEN
    _compare_workflows(workflow_old, output_old, output_new)


@pytest.mark.parametrize(
    "module_name",
    [
        "artifact_with_fanout",
        "artifact",
        "callable_dag",
        "daemon_nginx",
        "dag_custom_metrics",
        "dag_diamond",
        "dag_diamond_with_callable_container",
        "dag_nested",
        "dag_targets",
        "dag_task_level_timeout",
        "dynamic_fanout_container",
        "exit_handler_step_level",
        "loops_dag",
        "loops_maps",
        "loops_param_result",
        "loops",
        "map_reduce",
        "output_parameter",
        "parallelism_limit",
        "parallelism_nested",
        "parallelism_nested_dag",
        "parallelism_template_limit",
        "script_artifact_passing",
        "steps_with_callable_container",
        "suspend_template_outputs",
        "timeouts_workflow",
        "volume_mounts",
        "volume_mounts_wt",
        "workflow_event_binding__event_consumer_workflowtemplate",
    ],
)
# @pytest.mark.xfail
def test_regression_arguments_passing_containers(module_name):
    # GIVEN
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
    except KeyError:
        pass

    # THEN
    _compare_workflows(workflow_old, output_old, output_new)
