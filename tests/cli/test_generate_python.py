import os
from importlib.machinery import SourceFileLoader
from pathlib import Path
from types import ModuleType
from typing import cast

import pytest
from cappa.testing import CommandRunner

from hera._cli.base import Hera
from hera._cli.generate.python import python_obj_to_repr
from hera.workflows.cluster_workflow_template import ClusterWorkflowTemplate
from hera.workflows.cron_workflow import CronWorkflow
from hera.workflows.models import Metadata
from hera.workflows.workflow import Workflow
from hera.workflows.workflow_template import WorkflowTemplate
from tests.cli.test_generate_yaml import get_stdout
from tests.test_remaining_examples import UPSTREAM_EXAMPLES_FOLDER

runner = CommandRunner(Hera, base_args=["generate", "python"])

SKIP_FILES = [
    "cluster-workflow-template__clustertemplates.upstream.yaml",  # multiple workflows in one file
    "cron-backfill.upstream.yaml",  # multiple workflows in one file
    "memoize-simple.upstream.yaml",  # memoize not working
    "workflow-template__templates.upstream.yaml",  # multiple workflows in one file
    "workflow-event-binding__github-path-filter-workflowtemplate.upstream.yaml",  # value is a list (invalid?)
    "testvolume.upstream.yaml",  # not a workflow
    "configmaps__simple-parameters-configmap.upstream.yaml",  # not a workflow
    "workflow-event-binding__github-path-filter-workfloweventbinding.upstream.yaml",  # not a workflow
    "workflow-event-binding__event-consumer-workfloweventbinding.upstream.yaml",  # not a workflow
    "workflow-count-resourcequota.upstream.yaml",  # not a workflow
    "steps-inline-workflow.upstream.yaml",  # inline unsupported
    "dag-inline-workflow.upstream.yaml",  # inline unsupported
    "dag-inline-workflowtemplate.upstream.yaml",  # inline unsupported
    "dag-inline-clusterworkflowtemplate.upstream.yaml",  # inline unsupported
    "data-transformations.upstream.yaml",  # data template transformation field unsupported
    "dag-disable-failFast.upstream.yaml",  # fail fast is duplicated by the Argo spec itself, so we duplicate it in the roundtrip. This example otherwise generates correctly.
]


@pytest.mark.parametrize(
    "file_name",
    [
        pytest.param(
            f,
            marks=(
                pytest.mark.xfail(
                    reason="Multiple workflows in one yaml file not yet supported.\nYAML round trip issues for certain types.",
                    strict=True,
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

    loader = SourceFileLoader("workflow_output", str(output_path))
    workflow_module = ModuleType(loader.name)
    loader.exec_module(workflow_module)
    assert hasattr(workflow_module, "w") and isinstance(workflow_module.w, Workflow)
    workflow = workflow_module.w

    if isinstance(workflow, ClusterWorkflowTemplate):
        workflow_from_yaml = cast(ClusterWorkflowTemplate, ClusterWorkflowTemplate.from_file(yaml_file))
    elif isinstance(workflow, WorkflowTemplate):
        workflow_from_yaml = cast(WorkflowTemplate, WorkflowTemplate.from_file(yaml_file))
    elif isinstance(workflow, CronWorkflow):
        workflow_from_yaml = cast(CronWorkflow, CronWorkflow.from_file(yaml_file))
    else:
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


single_workflow_output = """\
from hera.workflows import Workflow
with Workflow(
api_version='argoproj.io/v1alpha1',
kind='Workflow',
name='single',
) as w:
    pass
"""

workflow_template_output = """\
from hera.workflows import WorkflowTemplate
with WorkflowTemplate(
api_version='argoproj.io/v1alpha1',
kind='WorkflowTemplate',
name='workflow-template',
) as w:
    pass
"""

cluster_workflow_template_output = """\
from hera.workflows import ClusterWorkflowTemplate
with ClusterWorkflowTemplate(
api_version='argoproj.io/v1alpha1',
kind='ClusterWorkflowTemplate',
name='cluster-workflow-template',
) as w:
    pass
"""

multiple_workflow_output = """\
from hera.workflows import Workflow
with Workflow(
api_version='argoproj.io/v1alpha1',
kind='Workflow',
name='one',
) as w:
    pass

from hera.workflows import Workflow
with Workflow(
api_version='argoproj.io/v1alpha1',
kind='Workflow',
name='two',
) as w:
    pass
"""

whole_folder_output = "\n".join(
    [
        cluster_workflow_template_output,
        multiple_workflow_output,
        single_workflow_output,
        workflow_template_output,
    ]
)


@pytest.mark.cli
def test_single_workflow(capsys):
    runner.invoke("tests/cli/examples/single_workflow.yaml")

    output = get_stdout(capsys)
    assert output == single_workflow_output


@pytest.mark.cli
def test_workflow_template(capsys):
    runner.invoke("tests/cli/examples/workflow_template.yaml")

    output = get_stdout(capsys)
    assert output == workflow_template_output


@pytest.mark.cli
def test_cluster_workflow_template(capsys):
    runner.invoke("tests/cli/examples/cluster_workflow_template.yaml")

    output = get_stdout(capsys)
    assert output == cluster_workflow_template_output


@pytest.mark.cli
def test_multiple_workflow(capsys):
    runner.invoke("tests/cli/examples/multiple_workflow.yaml")

    output = get_stdout(capsys)
    assert output == multiple_workflow_output


@pytest.mark.cli
def test_scan_folder(capsys):
    runner.invoke("tests/cli/examples")

    output = get_stdout(capsys)
    assert output == whole_folder_output


@pytest.mark.cli
def test_source_file_to_single_file(
    tmp_path: Path,
):
    output_file = tmp_path / "my_dir/foo.py"
    assert not output_file.parent.exists()  # ensure folder created

    runner.invoke("tests/cli/examples/single_workflow.yaml", "--to", str(output_file))

    assert output_file.parent.exists()
    assert output_file.exists()
    assert output_file.read_text() == single_workflow_output


@pytest.mark.cli
def test_source_folder_to_single_file(
    tmp_path: Path,
):
    output_file = tmp_path / "my_dir/foo.py"
    assert not output_file.parent.exists()

    runner.invoke("tests/cli/examples", "--to", str(output_file))

    assert output_file.exists()
    assert output_file.read_text() == whole_folder_output


@pytest.mark.cli
def test_source_file_to_output_folder(
    tmp_path: Path,
):
    runner.invoke("tests/cli/examples/single_workflow.yaml", "--to", str(tmp_path))

    assert (tmp_path / "single_workflow.py").exists()
    assert (tmp_path / "single_workflow.py").read_text() == single_workflow_output


@pytest.mark.cli
@pytest.mark.parametrize("recursive", [True, False])  # Should be the same in this case
def test_source_folder_to_output_folder(
    recursive: bool,
    tmp_path: Path,
):
    if recursive:
        runner.invoke("tests/cli/examples", "--recursive", "--to", str(tmp_path))
    else:
        runner.invoke("tests/cli/examples", "--to", str(tmp_path))

    assert (tmp_path / "cluster_workflow_template.py").exists()
    assert (tmp_path / "cluster_workflow_template.py").read_text() == cluster_workflow_template_output
    assert (tmp_path / "multiple_workflow.py").exists()
    assert (tmp_path / "multiple_workflow.py").read_text() == multiple_workflow_output
    assert (tmp_path / "single_workflow.py").exists()
    assert (tmp_path / "single_workflow.py").read_text() == single_workflow_output
    assert (tmp_path / "workflow_template.py").exists()
    assert (tmp_path / "workflow_template.py").read_text() == workflow_template_output


@pytest.mark.cli
def test_recursive_source_folder_to_output_folder_preserves_structure(
    tmp_path: Path,
):
    input_yaml = Path("tests/cli/examples/single_workflow.yaml").read_text()
    input_folder = tmp_path / "inputs"
    folder_1 = input_folder / "folder_1"
    folder_2 = input_folder / "folder_2"
    folder_3 = folder_2 / "folder_3"

    folder_1.mkdir(parents=True)
    folder_2.mkdir(parents=True)
    folder_3.mkdir(parents=True)

    for folder in [folder_1, folder_2, folder_3]:
        with (folder / "single_workflow.yaml").open("w") as file:
            file.write(input_yaml)

    output_folder = tmp_path / "outputs"
    runner.invoke(str(input_folder), "--recursive", "--to", str(output_folder))

    assert (output_folder / "folder_1/single_workflow.py").exists()
    assert (output_folder / "folder_1/single_workflow.py").read_text() == single_workflow_output
    assert (output_folder / "folder_2/single_workflow.py").exists()
    assert (output_folder / "folder_2/single_workflow.py").read_text() == single_workflow_output
    assert (output_folder / "folder_2/folder_3/single_workflow.py").exists()
    assert (output_folder / "folder_2/folder_3/single_workflow.py").read_text() == single_workflow_output


@pytest.mark.cli
def test_recursive_flatten_source_folder_to_output_folder_flattens_structure(
    tmp_path: Path,
):
    input_yaml = Path("tests/cli/examples/single_workflow.yaml").read_text()
    input_folder = tmp_path / "inputs"
    folder_1 = input_folder / "folder_1"
    folder_2 = input_folder / "folder_2"
    folder_3 = folder_2 / "folder_3"

    folder_1.mkdir(parents=True)
    folder_2.mkdir(parents=True)
    folder_3.mkdir(parents=True)

    for i, folder in enumerate([folder_1, folder_2, folder_3], start=1):
        with (folder / f"single_workflow_{i}.yaml").open("w") as file:
            file.write(input_yaml)

    output_folder = tmp_path / "outputs"
    runner.invoke(str(input_folder), "--recursive", "--flatten", "--to", str(output_folder))

    assert (output_folder / "single_workflow_1.py").exists()
    assert (output_folder / "single_workflow_1.py").read_text() == single_workflow_output
    assert (output_folder / "single_workflow_2.py").exists()
    assert (output_folder / "single_workflow_2.py").read_text() == single_workflow_output
    assert (output_folder / "single_workflow_3.py").exists()
    assert (output_folder / "single_workflow_3.py").read_text() == single_workflow_output
