import os
from importlib.machinery import SourceFileLoader
from pathlib import Path
from typing import cast

import pytest
from cappa.testing import CommandRunner

from hera._cli.base import Hera
from hera.workflows.workflow import Workflow

runner = CommandRunner(Hera, base_args=["generate", "python"])
UPSTREAM_EXAMPLES_FOLDER = Path("examples/workflows/upstream")


@pytest.mark.parametrize(
    "file_name",
    [
        f
        for f in os.listdir(UPSTREAM_EXAMPLES_FOLDER)
        if os.path.isfile(UPSTREAM_EXAMPLES_FOLDER / f) and f == "hello-world.upstream.yaml" # f.endswith(".upstream.yaml")
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
