import importlib
import os
import pkgutil
from pathlib import Path

import pytest
import requests
import yaml

import examples.workflows as hera_examples
import examples.workflows.upstream as hera_upstream_examples

ARGO_EXAMPLES_URL = "https://raw.githubusercontent.com/argoproj/argo-workflows/master/examples"
HERA_REGENERATE = os.environ.get("HERA_REGENERATE")
CI_MODE = os.environ.get("CI")


def _generate_yaml(path: Path) -> bool:
    if CI_MODE:
        return False
    if HERA_REGENERATE:
        return True
    return not path.exists()


@pytest.mark.parametrize(
    "module_name", [name for _, name, _ in pkgutil.iter_modules(hera_examples.__path__) if name != "upstream"]
)
def test_hera_output(module_name):
    # GIVEN
    workflow = importlib.import_module(f'examples.workflows.{module_name}').w
    yaml_path = Path(hera_examples.__file__).parent / f"{module_name.replace('_', '-')}.yaml"
    # WHEN
    output = workflow.to_dict()
    # THEN
    if _generate_yaml(yaml_path):
        yaml_path.write_text(yaml.dump(output))
    assert yaml_path.exists()
    assert output == yaml.safe_load(yaml_path.read_text())


@pytest.mark.parametrize("module_name", [name for _, name, _ in pkgutil.iter_modules(hera_upstream_examples.__path__)])
def test_hera_output_upstream(module_name):
    # GIVEN
    workflow = importlib.import_module(f'examples.workflows.upstream.{module_name}').w
    yaml_path = Path(hera_upstream_examples.__file__).parent / f"{module_name.replace('_', '-')}.yaml"
    upstream_yaml_path = (
        Path(hera_upstream_examples.__file__).parent / f"{module_name.replace('_', '-')}.upstream.yaml"
    )
    # WHEN
    output = workflow.to_dict()
    # THEN
    if _generate_yaml(yaml_path):
        yaml_path.write_text(yaml.dump(output))
    if _generate_yaml(upstream_yaml_path):
        upstream_yaml_path.write_text(requests.get(f"{ARGO_EXAMPLES_URL}/{module_name.replace('_', '-')}.yaml").text)
    assert yaml_path.exists()
    assert output == yaml.safe_load(yaml_path.read_text())
    assert upstream_yaml_path.exists()
    assert output == yaml.safe_load(upstream_yaml_path.read_text())
