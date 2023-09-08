import importlib

import pytest
from .test_examples import _compare_workflows


@pytest.mark.parametrize("module_name", ["script_artifact_passing"])
def test_script_annotations_parameter_regression(module_name):
    # GIVEN
    workflow_old = importlib.import_module(f"tests.output_references.{module_name}_old").w
    workflow_new = importlib.import_module(f"tests.output_references.{module_name}_new").w

    # WHEN
    output_old = workflow_old.to_dict()
    output_new = workflow_new.to_dict()

    # THEN
    _compare_workflows(workflow_old, output_old, output_new)
