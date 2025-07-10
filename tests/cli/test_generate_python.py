import os
from importlib.machinery import SourceFileLoader
from pathlib import Path
from typing import cast

import pytest
from cappa.testing import CommandRunner

from hera._cli.base import Hera
from hera._cli.generate.hera import python_obj_to_repr
from hera.workflows.models import Metadata
from hera.workflows.workflow import Workflow
from tests.test_remaining_examples import UPSTREAM_EXAMPLE_XFAIL_FILES, UPSTREAM_EXAMPLES_FOLDER

runner = CommandRunner(Hera, base_args=["generate", "python"])
SKIP_FILES = UPSTREAM_EXAMPLE_XFAIL_FILES + [
    "testvolume.upstream.yaml", # not a workflow
    "dag-disable-failFast.upstream.yaml", # fail fast is duplicated by the Argo spec, but otherwise works
    "steps-inline-workflow.upstream.yaml", # inline unsupported
    "dag-inline-workflow.upstream.yaml", # inline unsupported
    "configmaps__simple-parameters-configmap.upstream.yaml", # not a workflow
    "pod-metadata.upstream.yaml", # TODO: metadata (annotations/labels)
    "pod-gc-strategy-with-label-selector.upstream.yaml", # TODO: metadata (annotations/labels)
    "workflow-event-binding__github-path-filter-workfloweventbinding.upstream.yaml", # not a workflow
]


@pytest.mark.parametrize(
    "file_name",
    [
        pytest.param(
            f,
            marks=(
                pytest.mark.xfail(
                    reason="Multiple workflows in one yaml file not yet supported.\nYAML round trip issues for certain types."
                )
                if f in SKIP_FILES
                else ()
            ),
        )
        for f in os.listdir(UPSTREAM_EXAMPLES_FOLDER)
        if os.path.isfile(UPSTREAM_EXAMPLES_FOLDER / f) and f.endswith(".upstream.yaml")
    ],
)
def test_yaml_converter(file_name: str, tmp_path: Path):
    yaml_file = UPSTREAM_EXAMPLES_FOLDER / file_name

    output_path = tmp_path / "workflow_output.py"
    runner.invoke(str(yaml_file), "--to", str(output_path))

    workflow_module = SourceFileLoader("workflow_output", str(output_path)).load_module()

    assert hasattr(workflow_module, "w") and isinstance(workflow_module.w, Workflow)
    workflow = workflow_module.w

    workflow_from_yaml = cast(Workflow, Workflow.from_file(yaml_file))
    assert workflow.to_dict() == workflow_from_yaml.to_dict()


@pytest.mark.parametrize(
    "val,python_repr",
    [
        (
            1,
            "1",
        ),
        (1.01, "1.01"),
        (
            "Hello",
            "'Hello'",
        ),
        (
            True,
            "True",
        ),
        (
            [1, 2, 3],
            "[1, 2, 3]",
        ),
        (
            ["Hello", "world"],
            "['Hello', 'world']",
        ),
        (
            {"key": "value", "key2": 42},
            "{'key': 'value', 'key2': 42}",
        ),
    ],
)
def test_python_obj_to_repr(val: str, python_repr: str):
    """Basic types and lists/dicts should match the `repr` built-in."""
    assert python_obj_to_repr(val) == (python_repr, [], [])
    assert python_obj_to_repr(val) == (repr(val), [], [])


@pytest.mark.parametrize(
    "val,python_repr,expected_imports",
    [
        (
            Metadata(labels={"a-label": "value"}),
            "Metadata(labels={'a-label': 'value'},)",
            ["Metadata"],
        )
    ],
)
def test_python_obj_to_repr_with_models(val: str, python_repr: str, expected_imports: list[str]):
    assert python_obj_to_repr(val) == (python_repr, [], expected_imports)
