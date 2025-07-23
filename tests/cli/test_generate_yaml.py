import sys
from pathlib import Path
from textwrap import dedent
from unittest.mock import mock_open, patch

import pytest
from cappa.testing import CommandRunner

from hera._cli.base import Hera


def get_stdout(capsys):
    return capsys.readouterr().out


def join_output(*inputs):
    return "---\n".join(inputs)


def patch_open():
    if sys.version_info >= (3, 10) and sys.version_info <= (3, 11):
        return patch("pathlib._NormalAccessor.open", new=mock_open())
    return patch("io.open", new=mock_open())


single_workflow_output = """\
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  name: single
spec: {}
"""

runner_workflow_output = """\
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: runner-workflow-
spec:
  entrypoint: hello
  templates:
  - name: hello
    script:
      image: python:3.9
      source: '{{inputs.parameters}}'
      args:
      - -m
      - hera.workflows.runner
      - -e
      - tests.cli.examples.runner_workflow:hello
      command:
      - python
"""


workflow_template_output = """\
apiVersion: argoproj.io/v1alpha1
kind: WorkflowTemplate
metadata:
  name: workflow-template
spec: {}
"""

cluster_workflow_template_output = """\
apiVersion: argoproj.io/v1alpha1
kind: ClusterWorkflowTemplate
metadata:
  name: cluster-workflow-template
spec: {}
"""

multiple_workflow_output = """\
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  name: one
spec: {}
---
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  name: two
spec: {}
"""

whole_folder_output = join_output(
    cluster_workflow_template_output,
    multiple_workflow_output,
    single_workflow_output,
    workflow_template_output,
)


runner = CommandRunner(Hera, base_args=["generate", "yaml"])


@pytest.mark.cli
def test_no_output(capsys):
    runner.invoke("tests/cli/test_generate_yaml.py")

    output = get_stdout(capsys)
    expected_result = ""
    assert output == expected_result


@pytest.mark.cli
def test_single_workflow(capsys):
    runner.invoke("tests/cli/examples/single_workflow.py")

    output = get_stdout(capsys)
    assert output == single_workflow_output


@pytest.mark.cli
def test_runner_workflow(capsys):
    runner.invoke("tests/cli/examples/runner_workflow.py")

    output = get_stdout(capsys)
    assert output == runner_workflow_output


@pytest.mark.cli
def test_multiple_workflow(capsys):
    runner.invoke("tests/cli/examples/multiple_workflow.py")

    output = get_stdout(capsys)
    assert output == multiple_workflow_output


@pytest.mark.cli
def test_workflow_template(capsys):
    runner.invoke("tests/cli/examples/workflow_template.py")

    output = get_stdout(capsys)
    assert output == workflow_template_output


@pytest.mark.cli
def test_cluster_workflow_template(capsys):
    runner.invoke("tests/cli/examples/cluster_workflow_template.py")

    output = get_stdout(capsys)
    assert output == cluster_workflow_template_output


@pytest.mark.cli
def test_scan_folder(capsys):
    runner.invoke("tests/cli/examples")

    output = get_stdout(capsys)
    assert output == whole_folder_output


@pytest.mark.cli
def test_source_file_to_single_file(
    tmp_path: Path,
):
    output_file = tmp_path / "my_dir/foo.yaml"
    assert not output_file.parent.exists()  # ensure folder created

    runner.invoke("tests/cli/examples/single_workflow.py", "--to", str(output_file))

    assert output_file.parent.exists()
    assert output_file.exists()
    assert output_file.read_text() == single_workflow_output


@pytest.mark.cli
def test_source_folder_to_single_file(
    tmp_path: Path,
):
    output_file = tmp_path / "my_dir/foo.yaml"
    assert not output_file.parent.exists()

    runner.invoke("tests/cli/examples", "--to", str(output_file))

    assert output_file.exists()
    assert output_file.read_text() == whole_folder_output


@pytest.mark.cli
def test_source_file_to_output_folder(
    tmp_path: Path,
):
    runner.invoke("tests/cli/examples/single_workflow.py", "--to", str(tmp_path))

    assert (tmp_path / "single_workflow.yaml").exists()
    assert (tmp_path / "single_workflow.yaml").read_text() == single_workflow_output


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

    assert (tmp_path / "cluster_workflow_template.yaml").exists()
    assert (tmp_path / "cluster_workflow_template.yaml").read_text() == cluster_workflow_template_output
    assert (tmp_path / "multiple_workflow.yaml").exists()
    assert (tmp_path / "multiple_workflow.yaml").read_text() == multiple_workflow_output
    assert (tmp_path / "single_workflow.yaml").exists()
    assert (tmp_path / "single_workflow.yaml").read_text() == single_workflow_output
    assert (tmp_path / "workflow_template.yaml").exists()
    assert (tmp_path / "workflow_template.yaml").read_text() == workflow_template_output


@pytest.mark.cli
def test_recursive_source_folder_to_output_folder_preserves_structure(
    tmp_path: Path,
):
    input_python = Path("tests/cli/examples/single_workflow.py").read_text()
    input_folder = tmp_path / "inputs"
    folder_1 = input_folder / "folder_1"
    folder_2 = input_folder / "folder_2"
    folder_3 = folder_2 / "folder_3"

    folder_1.mkdir(parents=True)
    folder_2.mkdir(parents=True)
    folder_3.mkdir(parents=True)

    for folder in [folder_1, folder_2, folder_3]:
        with (folder / "single_workflow.py").open("w") as file:
            file.write(input_python)

    output_folder = tmp_path / "outputs"
    runner.invoke(str(input_folder), "--recursive", "--to", str(output_folder))

    assert (output_folder / "folder_1/single_workflow.yaml").exists()
    assert (output_folder / "folder_1/single_workflow.yaml").read_text() == single_workflow_output
    assert (output_folder / "folder_2/single_workflow.yaml").exists()
    assert (output_folder / "folder_2/single_workflow.yaml").read_text() == single_workflow_output
    assert (output_folder / "folder_2/folder_3/single_workflow.yaml").exists()
    assert (output_folder / "folder_2/folder_3/single_workflow.yaml").read_text() == single_workflow_output


@pytest.mark.cli
def test_recursive_flatten_source_folder_to_output_folder_flattens_structure(
    tmp_path: Path,
):
    input_python = Path("tests/cli/examples/single_workflow.py").read_text()
    input_folder = tmp_path / "inputs"
    folder_1 = input_folder / "folder_1"
    folder_2 = input_folder / "folder_2"
    folder_3 = folder_2 / "folder_3"

    folder_1.mkdir(parents=True)
    folder_2.mkdir(parents=True)
    folder_3.mkdir(parents=True)

    for i, folder in enumerate([folder_1, folder_2, folder_3], start=1):
        with (folder / f"single_workflow_{i}.py").open("w") as file:
            file.write(input_python)

    output_folder = tmp_path / "outputs"
    runner.invoke(str(input_folder), "--recursive", "--flatten", "--to", str(output_folder))

    assert (output_folder / "single_workflow_1.yaml").exists()
    assert (output_folder / "single_workflow_1.yaml").read_text() == single_workflow_output
    assert (output_folder / "single_workflow_2.yaml").exists()
    assert (output_folder / "single_workflow_2.yaml").read_text() == single_workflow_output
    assert (output_folder / "single_workflow_3.yaml").exists()
    assert (output_folder / "single_workflow_3.yaml").read_text() == single_workflow_output


@pytest.mark.cli
def test_recursive_flatten_source_folder_to_output_folder_with_name_clash_appends_to_file(
    tmp_path: Path,
):
    input_yaml = Path("tests/cli/examples/single_workflow.py").read_text()
    input_folder = tmp_path / "inputs"
    folder_1 = input_folder / "folder_1"
    folder_2 = input_folder / "folder_2"

    folder_1.mkdir(parents=True)
    folder_2.mkdir(parents=True)

    for i, folder in enumerate([folder_1, folder_2], start=1):
        with (folder / "single_workflow.py").open("w") as file:
            file.write(input_yaml)

    output_folder = tmp_path / "outputs"
    runner.invoke(str(input_folder), "--recursive", "--flatten", "--to", str(output_folder))

    assert (output_folder / "single_workflow.yaml").exists()
    assert (output_folder / "single_workflow.yaml").read_text() == "---\n".join([single_workflow_output] * 2)


@pytest.mark.cli
def test_relative_imports(capsys):
    runner.invoke("tests/cli/examples/relative_imports")

    output = get_stdout(capsys)
    assert output == dedent(
        """\
        apiVersion: argoproj.io/v1alpha1
        kind: Workflow
        metadata:
          name: relative_import
        spec:
          templates:
          - container:
              image: image
        """
    )


@pytest.mark.cli
def test_include_one(capsys):
    runner.invoke("tests/cli/examples", "--include=*/examples/single*")

    output = get_stdout(capsys)
    assert output == single_workflow_output


@pytest.mark.cli
def test_include_two(capsys):
    runner.invoke(
        "tests/cli/examples",
        "--include=*/examples/single*",
        "--include=*/examples/*template*",
    )

    output = get_stdout(capsys)
    assert output == join_output(
        cluster_workflow_template_output,
        single_workflow_output,
        workflow_template_output,
    )


@pytest.mark.cli
def test_exclude_one(capsys):
    runner.invoke("tests/cli/examples", "--exclude=*/examples/*template*")

    output = get_stdout(capsys)
    assert output == join_output(multiple_workflow_output, single_workflow_output)


@pytest.mark.cli
def test_exclude_two(capsys):
    runner.invoke(
        "tests/cli/examples",
        "--exclude=*/examples/single*",
        "--exclude=*/examples/*template*",
    )

    output = get_stdout(capsys)
    assert output == multiple_workflow_output


@pytest.mark.cli
def test_include_and_exclude(capsys):
    runner.invoke("tests/cli/examples", "--include=*/examples/*template*", "--exclude=*cluster*")

    output = get_stdout(capsys)
    assert output == workflow_template_output
