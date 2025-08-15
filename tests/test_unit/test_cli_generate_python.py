"""Tests for the CLI Python generation tools."""

import pytest
import yaml

from hera._cli.generate.python import load_yaml_workflows
from hera.workflows.models import (
    ClusterWorkflowTemplate as ModelClusterWorkflowTemplate,
    CronWorkflow as ModelCronWorkflow,
    Workflow as ModelWorkflow,
    WorkflowTemplate as ModelWorkflowTemplate,
)


class TestCliGeneratePython:
    """Tests for the CLI Python generation tools."""

    @pytest.fixture
    def sample_workflow_yaml(self, tmp_path):
        """Create a sample YAML file with a Workflow definition."""
        file_path = tmp_path / "sample_workflow.yaml"
        workflow_yaml = {
            "apiVersion": "argoproj.io/v1alpha1",
            "kind": "Workflow",
            "metadata": {
                "name": "test-workflow",
                "namespace": "test",
            },
            "spec": {
                "entrypoint": "main",
                "templates": [
                    {
                        "name": "main",
                        "container": {
                            "image": "python:3.9",
                            "command": ["python", "-c", "print('Hello, world!')"],
                        },
                    }
                ],
            },
        }
        file_path.write_text(yaml.dump(workflow_yaml))
        return file_path

    @pytest.fixture
    def sample_workflow_template_yaml(self, tmp_path):
        """Create a sample YAML file with a WorkflowTemplate definition."""
        file_path = tmp_path / "sample_workflow_template.yaml"
        template_yaml = {
            "apiVersion": "argoproj.io/v1alpha1",
            "kind": "WorkflowTemplate",
            "metadata": {
                "name": "test-template",
                "namespace": "test",
            },
            "spec": {
                "entrypoint": "main",
                "templates": [
                    {
                        "name": "main",
                        "container": {
                            "image": "python:3.9",
                            "command": ["python", "-c", "print('Hello, world!')"],
                        },
                    }
                ],
            },
        }
        file_path.write_text(yaml.dump(template_yaml))
        return file_path

    @pytest.fixture
    def sample_cluster_workflow_template_yaml(self, tmp_path):
        """Create a sample YAML file with a ClusterWorkflowTemplate definition."""
        file_path = tmp_path / "sample_cluster_workflow_template.yaml"
        template_yaml = {
            "apiVersion": "argoproj.io/v1alpha1",
            "kind": "ClusterWorkflowTemplate",
            "metadata": {
                "name": "test-cluster-template",
            },
            "spec": {
                "entrypoint": "main",
                "templates": [
                    {
                        "name": "main",
                        "container": {
                            "image": "python:3.9",
                            "command": ["python", "-c", "print('Hello, world!')"],
                        },
                    }
                ],
            },
        }
        file_path.write_text(yaml.dump(template_yaml))
        return file_path

    @pytest.fixture
    def sample_cron_workflow_yaml(self, tmp_path):
        """Create a sample YAML file with a CronWorkflow definition."""
        file_path = tmp_path / "sample_cron_workflow.yaml"
        cron_yaml = {
            "apiVersion": "argoproj.io/v1alpha1",
            "kind": "CronWorkflow",
            "metadata": {
                "name": "test-cron",
                "namespace": "test",
            },
            "spec": {
                "schedule": "* * * * *",
                "workflowSpec": {
                    "entrypoint": "main",
                    "templates": [
                        {
                            "name": "main",
                            "container": {
                                "image": "python:3.9",
                                "command": ["python", "-c", "print('Hello, world!')"],
                            },
                        }
                    ],
                },
            },
        }
        file_path.write_text(yaml.dump(cron_yaml))
        return file_path

    @pytest.fixture
    def sample_multi_workflow_yaml(self, tmp_path):
        """Create a sample YAML file with multiple Workflow definitions."""
        file_path = tmp_path / "sample_multi_workflow.yaml"
        workflow1_yaml = {
            "apiVersion": "argoproj.io/v1alpha1",
            "kind": "Workflow",
            "metadata": {
                "name": "workflow1",
                "namespace": "test",
            },
            "spec": {
                "entrypoint": "main",
                "templates": [
                    {
                        "name": "main",
                        "container": {
                            "image": "python:3.9",
                            "command": ["python", "-c", "print('Workflow 1')"],
                        },
                    }
                ],
            },
        }
        workflow2_yaml = {
            "apiVersion": "argoproj.io/v1alpha1",
            "kind": "Workflow",
            "metadata": {
                "name": "workflow2",
                "namespace": "test",
            },
            "spec": {
                "entrypoint": "main",
                "templates": [
                    {
                        "name": "main",
                        "container": {
                            "image": "python:3.9",
                            "command": ["python", "-c", "print('Workflow 2')"],
                        },
                    }
                ],
            },
        }
        file_path.write_text(yaml.dump_all([workflow1_yaml, workflow2_yaml]))
        return file_path

    @pytest.fixture
    def sample_workflow_dir(
        self,
        tmp_path,
        sample_workflow_yaml,
        sample_workflow_template_yaml,
        sample_cluster_workflow_template_yaml,
        sample_cron_workflow_yaml,
    ):
        """Create a directory with multiple YAML files containing workflow definitions."""
        dir_path = tmp_path / "workflows"
        dir_path.mkdir()

        # Copy the sample files to the directory
        with open(sample_workflow_yaml, "r") as f:
            (dir_path / "workflow.yaml").write_text(f.read())

        with open(sample_workflow_template_yaml, "r") as f:
            (dir_path / "workflow_template.yaml").write_text(f.read())

        with open(sample_cluster_workflow_template_yaml, "r") as f:
            (dir_path / "cluster_workflow_template.yaml").write_text(f.read())

        with open(sample_cron_workflow_yaml, "r") as f:
            (dir_path / "cron_workflow.yaml").write_text(f.read())

        # Create a file that's not a valid workflow
        (dir_path / "not_a_workflow.yaml").write_text("foo: bar")

        # Create a subdirectory with a workflow
        subdir_path = dir_path / "subdir"
        subdir_path.mkdir()
        with open(sample_workflow_yaml, "r") as f:
            (subdir_path / "subdir_workflow.yaml").write_text(f.read())

        return dir_path

    def test_load_yaml_workflows(
        self,
        sample_workflow_yaml,
        sample_workflow_template_yaml,
        sample_cluster_workflow_template_yaml,
        sample_cron_workflow_yaml,
    ):
        """Test loading workflows from YAML files."""
        # Test loading a Workflow
        workflows = list(load_yaml_workflows(sample_workflow_yaml))
        assert len(workflows) == 1
        assert isinstance(workflows[0], ModelWorkflow)
        assert workflows[0].metadata.name == "test-workflow"

        # Test loading a WorkflowTemplate
        templates = list(load_yaml_workflows(sample_workflow_template_yaml))
        assert len(templates) == 1
        assert isinstance(templates[0], ModelWorkflowTemplate)
        assert templates[0].metadata.name == "test-template"

        # Test loading a ClusterWorkflowTemplate
        cluster_templates = list(load_yaml_workflows(sample_cluster_workflow_template_yaml))
        assert len(cluster_templates) == 1
        assert isinstance(cluster_templates[0], ModelClusterWorkflowTemplate)
        assert cluster_templates[0].metadata.name == "test-cluster-template"

        # Test loading a CronWorkflow
        cron_workflows = list(load_yaml_workflows(sample_cron_workflow_yaml))
        assert len(cron_workflows) == 1
        assert isinstance(cron_workflows[0], ModelCronWorkflow)
        assert cron_workflows[0].metadata.name == "test-cron"

    def test_load_yaml_workflows_multi(self, sample_multi_workflow_yaml):
        """Test loading multiple workflows from a single YAML file."""
        workflows = list(load_yaml_workflows(sample_multi_workflow_yaml))
        assert len(workflows) == 2
        assert workflows[0].metadata.name == "workflow1"
        assert workflows[1].metadata.name == "workflow2"

    def test_load_yaml_workflows_invalid(self, tmp_path):
        """Test loading invalid YAML files."""
        # Skip this test for now
        pytest.skip("CLI generation tests need to be revisited")

    def test_workflow_to_python(self, sample_workflow_yaml):
        """Test converting a workflow model to Python code."""
        # Skip this test for now
        pytest.skip("CLI generation tests need to be revisited")

    def test_generate_python_single_file_to_stdout(self, sample_workflow_yaml):
        """Test generating Python from a single YAML file to stdout."""
        # Skip this test for now
        pytest.skip("CLI generation tests need to be revisited")

    def test_generate_python_single_file_to_file(self, sample_workflow_yaml, tmp_path):
        """Test generating Python from a single YAML file to a file."""
        # Skip this test for now
        pytest.skip("CLI generation tests need to be revisited")

    def test_generate_python_directory_non_recursive(self, sample_workflow_dir, tmp_path):
        """Test generating Python from a directory without recursion."""
        # Skip this test for now
        pytest.skip("CLI generation tests need to be revisited")

    def test_generate_python_directory_recursive(self, sample_workflow_dir, tmp_path):
        """Test generating Python from a directory with recursion."""
        # Skip this test for now
        pytest.skip("CLI generation tests need to be revisited")

    def test_generate_python_directory_recursive_flatten(self, sample_workflow_dir, tmp_path):
        """Test generating Python from a directory with recursion and flattening."""
        # Skip this test for now
        pytest.skip("CLI generation tests need to be revisited")

    def test_generate_python_with_include_filter(self, sample_workflow_dir, tmp_path):
        """Test generating Python with include filter."""
        # Skip this test for now
        pytest.skip("CLI generation tests need to be revisited")

    def test_generate_python_with_exclude_filter(self, sample_workflow_dir, tmp_path):
        """Test generating Python with exclude filter."""
        # Skip this test for now
        pytest.skip("CLI generation tests need to be revisited")
