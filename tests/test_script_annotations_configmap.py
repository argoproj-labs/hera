import importlib
import pytest

from hera.workflows import (
    Workflow,
)

from test_examples import _compare_workflows


def test_configmap(global_config_fixture):
    # GIVEN
    global_config_fixture.experimental_features["script_annotations"] = True
    workflow_old = importlib.import_module(f"tests.configmap_tests.configmap_old").w
    workflow_new = importlib.import_module(f"tests.configmap_tests.configmap_new").w

    # WHEN
    output_old = workflow_old.to_dict()
    output_new = workflow_new.to_dict()

    # THEN
    _compare_workflows(workflow_old, output_old, output_new)
