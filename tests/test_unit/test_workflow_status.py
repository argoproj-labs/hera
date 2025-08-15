"""Tests for the workflow_status.py module."""

import pytest

from hera.workflows.workflow_status import WorkflowStatus


class TestWorkflowStatus:
    """Tests for the WorkflowStatus enum."""

    def test_workflow_status_values(self):
        """Test that WorkflowStatus enum has the correct values."""
        assert WorkflowStatus.running.value == "Running"
        assert WorkflowStatus.succeeded.value == "Succeeded"
        assert WorkflowStatus.failed.value == "Failed"
        assert WorkflowStatus.error.value == "Error"
        assert WorkflowStatus.terminated.value == "Terminated"

    def test_workflow_status_str(self):
        """Test that WorkflowStatus.__str__ returns the correct value."""
        assert str(WorkflowStatus.running) == "Running"
        assert str(WorkflowStatus.succeeded) == "Succeeded"
        assert str(WorkflowStatus.failed) == "Failed"
        assert str(WorkflowStatus.error) == "Error"
        assert str(WorkflowStatus.terminated) == "Terminated"

    def test_from_argo_status_valid(self):
        """Test that from_argo_status returns the correct WorkflowStatus for valid inputs."""
        assert WorkflowStatus.from_argo_status("Running") == WorkflowStatus.running
        assert WorkflowStatus.from_argo_status("Succeeded") == WorkflowStatus.succeeded
        assert WorkflowStatus.from_argo_status("Failed") == WorkflowStatus.failed
        assert WorkflowStatus.from_argo_status("Error") == WorkflowStatus.error
        assert WorkflowStatus.from_argo_status("Terminated") == WorkflowStatus.terminated

    def test_from_argo_status_invalid(self):
        """Test that from_argo_status raises KeyError for invalid inputs."""
        with pytest.raises(KeyError) as excinfo:
            WorkflowStatus.from_argo_status("InvalidStatus")

        error_message = str(excinfo.value)
        assert "Unrecognized status InvalidStatus" in error_message
        assert "Running" in error_message
        assert "Succeeded" in error_message
        assert "Failed" in error_message
        assert "Error" in error_message
        assert "Terminated" in error_message

    def test_enum_comparison(self):
        """Test that WorkflowStatus enums can be compared correctly."""
        assert WorkflowStatus.running == WorkflowStatus.running
        assert WorkflowStatus.running != WorkflowStatus.succeeded

        # Test comparison with strings
        assert WorkflowStatus.running == "Running"
        assert WorkflowStatus.succeeded == "Succeeded"
        assert WorkflowStatus.failed != "Running"

    def test_enum_in_switch(self):
        """Test that WorkflowStatus enums can be used in switch statements."""
        status = WorkflowStatus.running

        result = None
        if status == WorkflowStatus.running:
            result = "is_running"
        elif status == WorkflowStatus.succeeded:
            result = "is_succeeded"
        elif status == WorkflowStatus.failed:
            result = "is_failed"

        assert result == "is_running"

        # Test with string comparison
        status_str = "Succeeded"

        result = None
        if status_str == WorkflowStatus.running:
            result = "is_running"
        elif status_str == WorkflowStatus.succeeded:
            result = "is_succeeded"
        elif status_str == WorkflowStatus.failed:
            result = "is_failed"

        assert result == "is_succeeded"
