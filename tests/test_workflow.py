import ast
import importlib
import os
import pkgutil
from pathlib import Path

import pytest
import requests
import yaml

import examples.workflows as hera_examples
import examples.workflows.upstream as hera_upstream_examples
from hera.workflows.models import Workflow

ARGO_EXAMPLES_URL = "https://raw.githubusercontent.com/argoproj/argo-workflows/master/examples"
HERA_REGENERATE = os.environ.get("HERA_REGENERATE")
CI_MODE = os.environ.get("CI")


def _generate_yaml(path: Path) -> bool:
    if CI_MODE:
        return False
    if HERA_REGENERATE:
        return True
    return not path.exists()


def _transform(obj):
    w = Workflow.parse_obj(obj)
    w.spec.templates.sort(key=lambda t: t.name)
    w.metadata.annotations = {}
    w.metadata.labels = {}
    for t in w.spec.templates:
        if t.script:
            t.script.source = ast.dump(ast.parse(t.script.source))
    return w.dict()


@pytest.mark.parametrize(
    "module_name", [name for _, name, _ in pkgutil.iter_modules(hera_examples.__path__) if name != "upstream"]
)
def test_hera_output(module_name):
    # GIVEN
    workflow = importlib.import_module(f"examples.workflows.{module_name}").w
    yaml_path = Path(hera_examples.__file__).parent / f"{module_name.replace('_', '-')}.yaml"
    # WHEN
    output = workflow.to_dict()
    # THEN
    if _generate_yaml(yaml_path):
        yaml_path.write_text(yaml.dump(output, sort_keys=False, default_flow_style=False))
    assert yaml_path.exists()
    assert output == yaml.safe_load(yaml_path.read_text())


@pytest.mark.parametrize("module_name", [name for _, name, _ in pkgutil.iter_modules(hera_upstream_examples.__path__)])
def test_hera_output_upstream(module_name):
    # GIVEN
    workflow = importlib.import_module(f"examples.workflows.upstream.{module_name}").w
    yaml_path = Path(hera_upstream_examples.__file__).parent / f"{module_name.replace('_', '-')}.yaml"
    upstream_yaml_path = (
        Path(hera_upstream_examples.__file__).parent / f"{module_name.replace('_', '-')}.upstream.yaml"
    )
    # WHEN
    output = workflow.to_dict()
    # THEN
    if _generate_yaml(yaml_path):
        yaml_path.write_text(yaml.dump(output, sort_keys=False, default_flow_style=False))
    if _generate_yaml(upstream_yaml_path):
        upstream_yaml_path.write_text(
            requests.get(f"{ARGO_EXAMPLES_URL}/{module_name.replace('__', '/').replace('_', '-')}.yaml").text
        )
    assert yaml_path.exists()
    assert output == yaml.safe_load(yaml_path.read_text())
    assert upstream_yaml_path.exists()
    assert _transform(output) == _transform(yaml.safe_load(upstream_yaml_path.read_text()))
