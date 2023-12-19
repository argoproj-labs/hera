import importlib
import os
import pkgutil
import sys
from pathlib import Path
from typing import Dict, List

import examples.workflows as hera_examples
import examples.workflows.upstream as hera_upstream_examples
import pytest
import requests
import yaml

from hera.workflows import (
    CronWorkflow as HeraCronWorkflow,
    Workflow as HeraWorkflow,
    WorkflowTemplate as HeraWorkflowTemplate,
)
from hera.workflows._unparse import roundtrip
from hera.workflows.models import (
    CronWorkflow as ModelCronWorkflow,
    Workflow as ModelWorkflow,
    WorkflowTemplate as ModelWorkflowTemplate,
)

ARGO_EXAMPLES_URL = "https://raw.githubusercontent.com/argoproj/argo-workflows/main/examples"
HERA_REGENERATE = os.environ.get("HERA_REGENERATE")
CI_MODE = os.environ.get("CI")

LOWEST_SUPPORTED_PY_VERSION = (3, 8)


def _generate_yaml(path: Path) -> bool:
    if sys.version_info[0] == LOWEST_SUPPORTED_PY_VERSION[0] and sys.version_info[1] > LOWEST_SUPPORTED_PY_VERSION[1]:
        # Generate yamls on lowest supported python version only
        return False
    if CI_MODE:
        return False
    if HERA_REGENERATE:
        return True
    return not path.exists()


def _transform_workflow(obj):
    w = ModelWorkflow.parse_obj(obj)
    w.metadata.annotations = {}
    w.metadata.labels = {}

    if w.spec.templates is not None:
        w.spec.templates.sort(key=lambda t: t.name)
        for t in w.spec.templates:
            if t.script:
                t.script.source = roundtrip(t.script.source)
    return w.dict()


def _transform_workflow_template(obj):
    w = ModelWorkflowTemplate.parse_obj(obj)
    w.metadata.annotations = {}
    w.metadata.labels = {}

    if w.spec.templates is not None:
        w.spec.templates.sort(key=lambda t: t.name)
        for t in w.spec.templates:
            if t.script:
                t.script.source = roundtrip(t.script.source)
    return w.dict()


def _transform_cron_workflow(obj):
    wt = ModelCronWorkflow.parse_obj(obj)
    wt.spec.workflow_spec.templates.sort(key=lambda t: t.name)
    wt.metadata.annotations = {}
    wt.metadata.labels = {}
    for t in wt.spec.workflow_spec.templates:
        if t.script:
            t.script.source = roundtrip(t.script.source)
    return wt.dict()


def _compare_workflows(hera_workflow, w1: Dict, w2: Dict):
    if isinstance(hera_workflow, HeraCronWorkflow):
        assert _transform_cron_workflow(w1) == _transform_cron_workflow(w2)
    elif isinstance(hera_workflow, HeraWorkflowTemplate):
        assert _transform_workflow_template(w1) == _transform_workflow_template(w2)
    elif isinstance(hera_workflow, HeraWorkflow):
        assert _transform_workflow(w1) == _transform_workflow(w2)
    else:
        assert False, f"Unsupported workflow type {hera_workflow}"


def _get_examples() -> List:
    """Return tuple of example's parent path, its full module and its filename (without ".py")."""
    modules = [
        (filefinder.path, module)
        for filefinder, module, ispkg in pkgutil.walk_packages(hera_examples.__path__, hera_examples.__name__ + ".")
        if not ispkg
    ]
    return [(path, module, module.split(".")[-1]) for path, module in modules if "upstream" not in module]


@pytest.mark.parametrize(
    "path,module_name,filename",
    [
        pytest.param(
            path,
            module_name,
            filename,
            id=filename,
        )
        for path, module_name, filename in _get_examples()
    ],
)
def test_hera_output(path, module_name, filename, global_config_fixture):
    # GIVEN
    global_config_fixture.host = "http://hera.testing"
    workflow = importlib.import_module(module_name).w
    generated_yaml_path = Path(path) / f"{filename.replace('_', '-')}.yaml"

    # WHEN
    output = workflow.to_dict()

    # THEN
    if _generate_yaml(generated_yaml_path):
        generated_yaml_path.write_text(yaml.dump(output, sort_keys=False, default_flow_style=False))

    # Check there have been no regressions from the generated yaml committed in the repo
    assert generated_yaml_path.exists()
    _compare_workflows(workflow, output, yaml.safe_load(generated_yaml_path.read_text()))

    if isinstance(workflow, HeraWorkflowTemplate):
        assert workflow == HeraWorkflowTemplate.from_dict(workflow.to_dict())
        assert workflow == HeraWorkflowTemplate.from_yaml(workflow.to_yaml())
    elif isinstance(workflow, HeraCronWorkflow):
        assert workflow == HeraCronWorkflow.from_dict(workflow.to_dict())
        assert workflow == HeraCronWorkflow.from_yaml(workflow.to_yaml())
    elif isinstance(workflow, HeraWorkflow):
        assert workflow == HeraWorkflow.from_dict(workflow.to_dict())
        assert workflow == HeraWorkflow.from_yaml(workflow.to_yaml())


@pytest.mark.parametrize("module_name", [name for _, name, _ in pkgutil.iter_modules(hera_upstream_examples.__path__)])
def test_hera_output_upstream(module_name, global_config_fixture):
    # GIVEN
    global_config_fixture.host = "http://hera.testing"
    workflow = importlib.import_module(f"examples.workflows.upstream.{module_name}").w
    generated_yaml_path = Path(hera_upstream_examples.__file__).parent / f"{module_name.replace('_', '-')}.yaml"
    upstream_yaml_path = Path(
        hera_upstream_examples.__file__
    ).parent / f"{module_name.replace('_', '-')}.upstream.yaml"

    # WHEN
    output = workflow.to_dict()

    # THEN - generate the yaml if HERA_REGENERATE or it does not exist
    if _generate_yaml(generated_yaml_path):
        generated_yaml_path.write_text(yaml.dump(output, sort_keys=False, default_flow_style=False))
    if _generate_yaml(upstream_yaml_path):
        upstream_yaml_path.write_text(
            requests.get(f"{ARGO_EXAMPLES_URL}/{module_name.replace('__', '/').replace('_', '-')}.yaml").text
        )

    # Check there have been no regressions from the generated yaml
    assert generated_yaml_path.exists()
    _compare_workflows(workflow, output, yaml.safe_load(generated_yaml_path.read_text()))

    # Check there have been no regressions with the upstream source
    assert upstream_yaml_path.exists()
    _compare_workflows(workflow, output, yaml.safe_load(upstream_yaml_path.read_text()))

    if isinstance(workflow, HeraWorkflowTemplate):
        assert workflow == HeraWorkflowTemplate.from_dict(workflow.to_dict())
        assert workflow == HeraWorkflowTemplate.from_yaml(workflow.to_yaml())
    elif isinstance(workflow, HeraCronWorkflow):
        assert workflow == HeraCronWorkflow.from_dict(workflow.to_dict())
        assert workflow == HeraCronWorkflow.from_yaml(workflow.to_yaml())
    elif isinstance(workflow, HeraWorkflow):
        assert workflow == HeraWorkflow.from_dict(workflow.to_dict())
        assert workflow == HeraWorkflow.from_yaml(workflow.to_yaml())
