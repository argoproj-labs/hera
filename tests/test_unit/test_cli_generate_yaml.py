"""Tests for the CLI YAML generation tools."""

from unittest.mock import patch

import pytest
import yaml

from hera._cli.base import GenerateYaml
from hera._cli.generate.yaml import generate_yaml, load_workflows_from_module
from hera.workflows.workflow import Workflow


class TestCliGenerateYaml:
    """Tests for the CLI YAML generation tools."""

    @pytest.fixture
    def sample_workflow_file(self, tmp_path):
        """Create a sample Python file with a Workflow definition."""
        file_path = tmp_path / "sample_workflow.py"
        file_path.write_text(
            """
from hera.workflows import Workflow

with Workflow(name="test-workflow", namespace="test") as w:
    pass
"""
        )
        return file_path

    @pytest.fixture
    def sample_workflow_dir(self, tmp_path):
        """Create a directory with multiple Python files containing Workflow definitions."""
        dir_path = tmp_path / "workflows"
        dir_path.mkdir()

        # Create a file with a workflow
        file1_path = dir_path / "workflow1.py"
        file1_path.write_text(
            """
from hera.workflows import Workflow

with Workflow(name="workflow1", namespace="test") as w:
    pass
"""
        )

        # Create a file with multiple workflows
        file2_path = dir_path / "workflow2.py"
        file2_path.write_text(
            """
from hera.workflows import Workflow

with Workflow(name="workflow2a", namespace="test") as w1:
    pass

with Workflow(name="workflow2b", namespace="test") as w2:
    pass
"""
        )

        # Create a file without workflows
        file3_path = dir_path / "not_a_workflow.py"
        file3_path.write_text(
            """
def hello():
    print("Hello, world!")
"""
        )

        # Create a subdirectory with a workflow
        subdir_path = dir_path / "subdir"
        subdir_path.mkdir()
        file4_path = subdir_path / "workflow3.py"
        file4_path.write_text(
            """
from hera.workflows import Workflow

with Workflow(name="workflow3", namespace="test") as w:
    pass
"""
        )

        return dir_path

    def test_load_workflows_from_module(self, sample_workflow_file):
        """Test loading workflows from a Python module."""
        workflows = list(load_workflows_from_module(sample_workflow_file))
        assert len(workflows) == 1
        assert isinstance(workflows[0], Workflow)
        assert workflows[0].name == "test-workflow"
        assert workflows[0].namespace == "test"

    def test_generate_yaml_single_file_to_stdout(self, sample_workflow_file):
        """Test generating YAML from a single Python file to stdout."""
        options = GenerateYaml(
            from_=sample_workflow_file,
            to=None,
            recursive=False,
            flatten=False,
            include=[],
            exclude=[],
        )

        with patch("sys.stdout.write") as mock_write:
            generate_yaml(options)
            mock_write.assert_called_once()
            yaml_output = mock_write.call_args[0][0]

            # Parse the YAML to verify it's valid
            parsed_yaml = yaml.safe_load(yaml_output)
            assert parsed_yaml["kind"] == "Workflow"
            assert parsed_yaml["metadata"]["name"] == "test-workflow"
            assert parsed_yaml["metadata"]["namespace"] == "test"

    def test_generate_yaml_single_file_to_file(self, sample_workflow_file, tmp_path):
        """Test generating YAML from a single Python file to a file."""
        output_file = tmp_path / "output.yaml"
        options = GenerateYaml(
            from_=sample_workflow_file,
            to=output_file,
            recursive=False,
            flatten=False,
            include=[],
            exclude=[],
        )

        generate_yaml(options)

        assert output_file.exists()
        yaml_output = output_file.read_text()

        # Parse the YAML to verify it's valid
        parsed_yaml = yaml.safe_load(yaml_output)
        assert parsed_yaml["kind"] == "Workflow"
        assert parsed_yaml["metadata"]["name"] == "test-workflow"
        assert parsed_yaml["metadata"]["namespace"] == "test"

    def test_generate_yaml_directory_non_recursive(self, sample_workflow_dir, tmp_path):
        """Test generating YAML from a directory without recursion."""
        output_dir = tmp_path / "output"
        options = GenerateYaml(
            from_=sample_workflow_dir,
            to=output_dir,
            recursive=False,
            flatten=False,
            include=[],
            exclude=[],
        )

        generate_yaml(options)

        assert output_dir.exists()
        assert (output_dir / "workflow1.yaml").exists()
        assert (output_dir / "workflow2.yaml").exists()
        assert not (output_dir / "not_a_workflow.yaml").exists()  # No workflows in this file
        assert not (output_dir / "subdir").exists()  # Not recursive

        # Check workflow1.yaml
        yaml_output = (output_dir / "workflow1.yaml").read_text()
        parsed_yaml = yaml.safe_load(yaml_output)
        assert parsed_yaml["metadata"]["name"] == "workflow1"

        # Check workflow2.yaml (should have two workflows)
        yaml_output = (output_dir / "workflow2.yaml").read_text()
        parsed_yamls = list(yaml.safe_load_all(yaml_output))
        assert len(parsed_yamls) == 2
        assert parsed_yamls[0]["metadata"]["name"] == "workflow2a"
        assert parsed_yamls[1]["metadata"]["name"] == "workflow2b"

    def test_generate_yaml_directory_recursive(self, sample_workflow_dir, tmp_path):
        """Test generating YAML from a directory with recursion."""
        output_dir = tmp_path / "output"
        options = GenerateYaml(
            from_=sample_workflow_dir,
            to=output_dir,
            recursive=True,
            flatten=False,
            include=[],
            exclude=[],
        )

        generate_yaml(options)

        assert output_dir.exists()
        assert (output_dir / "workflow1.yaml").exists()
        assert (output_dir / "workflow2.yaml").exists()
        assert not (output_dir / "not_a_workflow.yaml").exists()  # No workflows in this file
        assert (output_dir / "subdir").exists()
        assert (output_dir / "subdir" / "workflow3.yaml").exists()

        # Check subdir/workflow3.yaml
        yaml_output = (output_dir / "subdir" / "workflow3.yaml").read_text()
        parsed_yaml = yaml.safe_load(yaml_output)
        assert parsed_yaml["metadata"]["name"] == "workflow3"

    def test_generate_yaml_directory_recursive_flatten(self, sample_workflow_dir, tmp_path):
        """Test generating YAML from a directory with recursion and flattening."""
        output_dir = tmp_path / "output"
        options = GenerateYaml(
            from_=sample_workflow_dir,
            to=output_dir,
            recursive=True,
            flatten=True,
            include=[],
            exclude=[],
        )

        generate_yaml(options)

        assert output_dir.exists()
        assert (output_dir / "workflow1.yaml").exists()
        assert (output_dir / "workflow2.yaml").exists()
        assert not (output_dir / "not_a_workflow.yaml").exists()  # No workflows in this file
        assert (output_dir / "workflow3.yaml").exists()  # Flattened
        assert not (output_dir / "subdir").exists()  # Flattened

        # Check workflow3.yaml
        yaml_output = (output_dir / "workflow3.yaml").read_text()
        parsed_yaml = yaml.safe_load(yaml_output)
        assert parsed_yaml["metadata"]["name"] == "workflow3"

    def test_generate_yaml_with_include_filter(self, sample_workflow_dir, tmp_path):
        """Test generating YAML with include filter."""
        output_dir = tmp_path / "output"
        options = GenerateYaml(
            from_=sample_workflow_dir,
            to=output_dir,
            recursive=False,
            flatten=False,
            include=["*workflow1.py"],
            exclude=[],
        )

        generate_yaml(options)

        assert output_dir.exists()
        assert (output_dir / "workflow1.yaml").exists()
        assert not (output_dir / "workflow2.yaml").exists()  # Filtered out

    def test_generate_yaml_with_exclude_filter(self, sample_workflow_dir, tmp_path):
        """Test generating YAML with exclude filter."""
        output_dir = tmp_path / "output"
        options = GenerateYaml(
            from_=sample_workflow_dir,
            to=output_dir,
            recursive=False,
            flatten=False,
            include=[],
            exclude=["*workflow1.py"],
        )

        generate_yaml(options)

        assert output_dir.exists()
        assert not (output_dir / "workflow1.yaml").exists()  # Filtered out
        assert (output_dir / "workflow2.yaml").exists()
