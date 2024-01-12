import sys
from textwrap import dedent
from unittest.mock import mock_open, patch

import pytest
from cappa.testing import CommandRunner

from hera._cli.base import Hera


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
def test_source_file_output_file():
    exists_patch = patch("os.path.exists", return_value=True)
    write_text_patch = patch("pathlib.Path.write_text")

    with exists_patch, write_text_patch as m:
        runner.invoke("tests/cli/examples/single_workflow.py", "--to", "foo.yml")

    assert m.call_count == 1

    output = m.mock_calls[0][1][0]
    assert output == single_workflow_output


@pytest.mark.cli
def test_source_folder_output_file():
    exists_patch = patch("os.path.exists", return_value=True)
    is_file_patch = patch("pathlib.Path.is_file", return_value=True)
    write_text_patch = patch("pathlib.Path.write_text")

    with exists_patch, is_file_patch, write_text_patch as m:
        runner.invoke("tests/cli/examples", "--to", "foo.yml")

    assert m.call_count == 1

    output = m.mock_calls[0][1][0]
    assert output == whole_folder_output


@pytest.mark.cli
def test_source_file_output_folder():
    source_is_dir_patch = patch("pathlib.Path.is_dir", return_value=False)
    dest_exists_patch = patch("os.path.exists", return_value=True)
    dest_is_file_patch = patch("pathlib.Path.is_file", return_value=False)
    makedirs_patch = patch("os.makedirs")

    open_patch = patch_open()

    with source_is_dir_patch, dest_exists_patch, dest_is_file_patch, makedirs_patch, open_patch:
        runner.invoke("tests/cli/examples/single_workflow.py", "--to", "dir/")

    filename = str(open_patch.new.mock_calls[0][1][0])
    assert filename == "dir/single_workflow.yaml"

    content = open_patch.new.return_value.write.mock_calls[0][1][0]
    assert content == single_workflow_output


@pytest.mark.cli
def test_source_folder_output_folder():
    source_is_dir_patch = patch("pathlib.Path.is_dir", return_value=True)
    dest_exists_patch = patch("os.path.exists", return_value=False)
    makedirs_patch = patch("os.makedirs")

    open_patch = patch_open()

    with source_is_dir_patch, dest_exists_patch, makedirs_patch, open_patch:
        runner.invoke("tests/cli/examples", "--to", "dir/")

    assert open_patch.new.call_count == 4
    assert open_patch.new.return_value.write.call_count == 4

    filenames = [
        str(open_patch.new.mock_calls[0][1][0]),
        str(open_patch.new.mock_calls[4][1][0]),
        str(open_patch.new.mock_calls[8][1][0]),
        str(open_patch.new.mock_calls[12][1][0]),
    ]
    assert filenames == [
        "dir/cluster_workflow_template.yaml",
        "dir/multiple_workflow.yaml",
        "dir/single_workflow.yaml",
        "dir/workflow_template.yaml",
    ]

    content1 = open_patch.new.return_value.write.mock_calls[1][1][0]
    assert content1 == multiple_workflow_output

    content2 = open_patch.new.return_value.write.mock_calls[2][1][0]
    assert content2 == single_workflow_output


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
