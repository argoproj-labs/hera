import importlib
import pytest


from test_examples import _compare_workflows

try:
    from typing import Annotated  # type: ignore
except ImportError:
    from typing_extensions import Annotated  # type: ignore

from hera.workflows import Workflow, script
from hera.workflows.steps import Steps
from hera.workflows.parameter import Parameter


@pytest.mark.parametrize("module_name", ["combined", "default", "description", "enum"])
def test_hera_output(module_name, global_config_fixture):
    # GIVEN
    global_config_fixture.experimental_features["script_annotations"] = True
    workflow_old = importlib.import_module(f"examples.workflows.script_annotations_{module_name}_old").w
    workflow_new = importlib.import_module(f"examples.workflows.script_annotations_{module_name}_new").w

    # WHEN
    output_old = workflow_old.to_dict()
    output_new = workflow_new.to_dict()

    # THEN
    _compare_workflows(workflow_old, output_old, output_new)


@script()
def echo_int(an_int: Annotated[int, Parameter(default=1)] = 2):
    print(an_int)


def test_double_default(global_config_fixture):
    global_config_fixture.experimental_features["script_annotations"] = True
    with pytest.raises(ValueError) as e:
        with Workflow(generate_name="test-types-", entrypoint="my_steps") as w:
            with Steps(name="my_steps"):
                echo_int()

        w.to_dict()

    assert "The default cannot be set via both the function parameter default and the annotation's default" in str(
        e.value
    )
