from textwrap import dedent
from unittest.mock import mock_open, patch

import cappa
import pytest

from hera._cli.base import Hera


def get_stdout(capsys):
    return capsys.readouterr().out


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

whole_folder_output = "\n---\n\n".join(
    [
        cluster_workflow_template_output,
        multiple_workflow_output,
        single_workflow_output,
        workflow_template_output,
    ]
)


@pytest.mark.cli
def test_no_output(capsys):
    cappa.invoke(Hera, argv=["generate", "yaml", "tests/cli/test_generate_yaml.py"])

    output = get_stdout(capsys)
    expected_result = ""
    assert output == expected_result


@pytest.mark.cli
def test_single_workflow(capsys):
    cappa.invoke(Hera, argv=["generate", "yaml", "tests/cli/examples/single_workflow.py"])

    output = get_stdout(capsys)
    assert output == single_workflow_output


@pytest.mark.cli
def test_multiple_workflow(capsys):
    cappa.invoke(Hera, argv=["generate", "yaml", "tests/cli/examples/multiple_workflow.py"])

    output = get_stdout(capsys)
    assert output == multiple_workflow_output


@pytest.mark.cli
def test_workflow_template(capsys):
    cappa.invoke(Hera, argv=["generate", "yaml", "tests/cli/examples/workflow_template.py"])

    output = get_stdout(capsys)
    assert output == workflow_template_output


@pytest.mark.cli
def test_cluster_workflow_template(capsys):
    cappa.invoke(
        Hera,
        argv=["generate", "yaml", "tests/cli/examples/cluster_workflow_template.py"],
    )

    output = get_stdout(capsys)
    assert output == cluster_workflow_template_output


@pytest.mark.cli
def test_scan_folder(capsys):
    cappa.invoke(Hera, argv=["generate", "yaml", "tests/cli/examples"])

    output = get_stdout(capsys)
    assert output == whole_folder_output


@pytest.mark.cli
def test_source_file_output_file():
    exists_patch = patch("os.path.exists", return_value=True)
    write_text_patch = patch("pathlib.Path.write_text")

    with exists_patch, write_text_patch as m:
        cappa.invoke(
            Hera,
            argv=[
                "generate",
                "yaml",
                "tests/cli/examples/single_workflow.py",
                "--to",
                "foo.yml",
            ],
        )

    assert m.call_count == 1

    output = m.mock_calls[0][1][0]
    assert output == single_workflow_output


@pytest.mark.cli
def test_source_folder_output_file():
    exists_patch = patch("os.path.exists", return_value=True)
    is_file_patch = patch("pathlib.Path.is_file", return_value=True)
    write_text_patch = patch("pathlib.Path.write_text")

    with exists_patch, is_file_patch, write_text_patch as m:
        cappa.invoke(
            Hera,
            argv=[
                "generate",
                "yaml",
                "tests/cli/examples",
                "--to",
                "foo.yml",
            ],
        )

    assert m.call_count == 1

    output = m.mock_calls[0][1][0]
    assert output == whole_folder_output


@pytest.mark.cli
def test_source_file_output_folder():
    source_is_dir_patch = patch("pathlib.Path.is_dir", return_value=False)
    dest_exists_patch = patch("os.path.exists", return_value=True)
    dest_is_file_patch = patch("pathlib.Path.is_file", return_value=False)
    makedirs_patch = patch("os.makedirs")

    open_patch = patch("io.open", new=mock_open())

    with source_is_dir_patch, dest_exists_patch, dest_is_file_patch, makedirs_patch, open_patch:
        cappa.invoke(
            Hera,
            argv=[
                "generate",
                "yaml",
                "tests/cli/examples/single_workflow.py",
                "--to",
                "dir/",
            ],
        )

    filename = str(open_patch.new.mock_calls[0][1][0])
    assert filename == "dir/single_workflow.yaml"

    content = open_patch.new.return_value.write.mock_calls[0][1][0]
    assert content == single_workflow_output


@pytest.mark.cli
def test_source_folder_output_folder():
    source_is_dir_patch = patch("pathlib.Path.is_dir", return_value=True)
    dest_exists_patch = patch("os.path.exists", return_value=False)
    makedirs_patch = patch("os.makedirs")

    open_patch = patch("io.open", new=mock_open())

    with source_is_dir_patch, dest_exists_patch, makedirs_patch, open_patch:
        cappa.invoke(
            Hera,
            argv=[
                "generate",
                "yaml",
                "tests/cli/examples",
                "--to",
                "dir/",
            ],
        )

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
