import os
from pathlib import Path
import sys
from textwrap import dedent
from unittest.mock import MagicMock, call, mock_open, patch

import pytest
from cappa.testing import CommandRunner

from hera._cli.base import Hera
from hera._cli.generate.yaml import _write_workflow_to_yaml


def get_stdout(capsys):
    return capsys.readouterr().out


def join_output(*inputs):
    return "\n---\n\n".join(inputs)


def patch_open():
    if sys.version_info >= (3, 10) and sys.version_info <= (3, 11):
        return patch("pathlib._NormalAccessor.open", new=mock_open())
    return patch("io.open", new=mock_open())


single_workflow_output = dedent(
    """\
        apiVersion: argoproj.io/v1alpha1
        kind: Workflow
        metadata:
          name: single
        spec: {}
        """
)

workflow_template_output = dedent(
    """\
            apiVersion: argoproj.io/v1alpha1
            kind: WorkflowTemplate
            metadata:
              name: workflow-template
            spec: {}
            """
)

cluster_workflow_template_output = dedent(
    """\
            apiVersion: argoproj.io/v1alpha1
            kind: ClusterWorkflowTemplate
            metadata:
              name: cluster-workflow-template
            spec: {}
            """
)

multiple_workflow_output = dedent(
    """\
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
)

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
def test_write_workflow_to_yaml(tmp_path: Path):
    string = "text for test"
    filepath = tmp_path / "test.txt"
    _write_workflow_to_yaml(filepath, string)
    assert filepath.read_text() == string


@pytest.mark.cli
@patch("hera._cli.generate.yaml._write_workflow_to_yaml")
@patch("hera._cli.generate.yaml.os")
def test_source_file_to_single_file(
    mock_os: MagicMock,
    mock_write_workflow_to_yaml: MagicMock,
):
    makedirs_mock = MagicMock()
    mock_os.makedirs = makedirs_mock

    runner.invoke("tests/cli/examples/single_workflow.py", "--to", "foo.yaml")

    makedirs_mock.assert_called_once_with(Path("foo.yaml").parent, exist_ok=True)
    mock_write_workflow_to_yaml.assert_called_once_with(Path("foo.yaml"), single_workflow_output)


@pytest.mark.cli
@patch("hera._cli.generate.yaml._write_workflow_to_yaml")
@patch("hera._cli.generate.yaml.os")
def test_source_folder_to_single_file(
    mock_os: MagicMock,
    mock_write_workflow_to_yaml: MagicMock,
):
    mock_os.walk = os.walk
    mock_os.path.join = os.path.join

    makedirs_mock = MagicMock()
    mock_os.makedirs = makedirs_mock

    runner.invoke("tests/cli/examples", "--to", "foo.yaml")

    makedirs_mock.assert_called_once_with(Path("foo.yaml").parent, exist_ok=True)
    mock_write_workflow_to_yaml.assert_called_once_with(Path("foo.yaml"), whole_folder_output)


@pytest.mark.cli
@patch("hera._cli.generate.yaml._write_workflow_to_yaml")
@patch("hera._cli.generate.yaml.os")
def test_source_file_to_output_folder(
    mock_os: MagicMock,
    mock_write_workflow_to_yaml: MagicMock,
):
    makedirs_mock = MagicMock()
    mock_os.makedirs = makedirs_mock

    runner.invoke("tests/cli/examples/single_workflow.py", "--to", "dir/")

    makedirs_mock.assert_called_once_with(Path("dir/"), exist_ok=True)
    mock_write_workflow_to_yaml.assert_called_once_with(Path("dir/single_workflow.yaml"), single_workflow_output)


@pytest.mark.cli
@patch("hera._cli.generate.yaml._write_workflow_to_yaml")
@patch("hera._cli.generate.yaml.os")
def test_source_folder_to_output_folder(
    mock_os: MagicMock,
    mock_write_workflow_to_yaml: MagicMock,
):
    mock_os.walk = os.walk
    mock_os.path.join = os.path.join

    makedirs_mock = MagicMock()
    mock_os.makedirs = makedirs_mock

    runner.invoke("tests/cli/examples", "--to", "dir/")

    makedirs_mock.assert_called_once_with(Path("dir/"), exist_ok=True)
    mock_write_workflow_to_yaml.assert_has_calls(
        [
            call(Path("dir/cluster_workflow_template.yaml"), cluster_workflow_template_output),
            call(Path("dir/multiple_workflow.yaml"), multiple_workflow_output),
            call(Path("dir/single_workflow.yaml"), single_workflow_output),
            call(Path("dir/workflow_template.yaml"), workflow_template_output),
        ],
        any_order=True,
    )


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
