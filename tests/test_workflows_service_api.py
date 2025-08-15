"""Tests for the WorkflowsService API methods."""

from unittest.mock import MagicMock

import pytest
import requests

from hera.exceptions import NotFound
from hera.workflows.models import (
    ClusterWorkflowTemplate,
    ClusterWorkflowTemplateCreateRequest,
    ClusterWorkflowTemplateList,
    CreateCronWorkflowRequest,
    CronWorkflow,
    CronWorkflowList,
    InfoResponse,
    Workflow,
    WorkflowCreateRequest,
    WorkflowList,
    WorkflowTemplate,
    WorkflowTemplateCreateRequest,
    WorkflowTemplateList,
)
from hera.workflows.service import WorkflowsService


class TestWorkflowsServiceAPI:
    """Tests for the WorkflowsService API methods."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock session for testing."""
        session = MagicMock(spec=requests.Session)
        response = MagicMock(spec=requests.Response)
        response.ok = True
        response.json.return_value = {}
        session.request.return_value = response
        return session

    @pytest.fixture
    def service(self, mock_session):
        """Create a service with a mock session."""
        return WorkflowsService(
            host="https://localhost:2746",
            namespace="argo",
            session=mock_session,
        )

    def test_valid_host_scheme(self):
        """Test the valid_host_scheme function."""
        from hera.workflows.service import valid_host_scheme

        assert valid_host_scheme("http://localhost") is True
        assert valid_host_scheme("https://localhost") is True
        assert valid_host_scheme("localhost") is False
        assert valid_host_scheme("ftp://localhost") is False

    def test_list_workflows(self, service, mock_session):
        """Test the list_workflows method."""
        mock_session.request.return_value.json.return_value = {
            "items": [],
            "metadata": {"resourceVersion": "42"},
        }

        result = service.list_workflows()

        assert isinstance(result, WorkflowList)
        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        assert call_args[0][0] == "get"
        assert call_args[1]["url"] == "https://localhost:2746/api/v1/workflows/argo"

    def test_create_workflow(self, service, mock_session):
        """Test the create_workflow method."""
        mock_session.request.return_value.json.return_value = {
            "metadata": {"name": "test-workflow", "namespace": "argo"},
            "spec": {},
            "status": {},
        }

        req = WorkflowCreateRequest(
            workflow=Workflow(metadata={"name": "test-workflow"}, spec={"entrypoint": "main", "templates": []})
        )
        result = service.create_workflow(req)

        assert isinstance(result, Workflow)
        assert result.metadata.name == "test-workflow"
        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        assert call_args[0][0] == "post"
        assert call_args[1]["url"] == "https://localhost:2746/api/v1/workflows/argo"

    def test_get_workflow(self, service, mock_session):
        """Test the get_workflow method."""
        mock_session.request.return_value.json.return_value = {
            "metadata": {"name": "test-workflow", "namespace": "argo"},
            "spec": {},
            "status": {},
        }

        result = service.get_workflow("test-workflow")

        assert isinstance(result, Workflow)
        assert result.metadata.name == "test-workflow"
        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        assert call_args[0][0] == "get"
        assert call_args[1]["url"] == "https://localhost:2746/api/v1/workflows/argo/test-workflow"

    def test_list_cron_workflows(self, service, mock_session):
        """Test the list_cron_workflows method."""
        mock_session.request.return_value.json.return_value = {
            "items": [],
            "metadata": {"resourceVersion": "42"},
        }

        result = service.list_cron_workflows()

        assert isinstance(result, CronWorkflowList)
        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        assert call_args[0][0] == "get"
        assert call_args[1]["url"] == "https://localhost:2746/api/v1/cron-workflows/argo"

    def test_create_cron_workflow(self, service, mock_session):
        """Test the create_cron_workflow method."""
        mock_session.request.return_value.json.return_value = {
            "metadata": {"name": "test-cron", "namespace": "argo"},
            "spec": {"schedule": "* * * * *", "workflowSpec": {"entrypoint": "main", "templates": []}},
        }

        req = CreateCronWorkflowRequest(
            cron_workflow=CronWorkflow(
                metadata={"name": "test-cron"},
                spec={"schedule": "* * * * *", "workflowSpec": {"entrypoint": "main", "templates": []}},
            )
        )
        result = service.create_cron_workflow(req)

        assert isinstance(result, CronWorkflow)
        assert result.metadata.name == "test-cron"
        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        assert call_args[0][0] == "post"
        assert call_args[1]["url"] == "https://localhost:2746/api/v1/cron-workflows/argo"

    def test_list_workflow_templates(self, service, mock_session):
        """Test the list_workflow_templates method."""
        mock_session.request.return_value.json.return_value = {
            "items": [],
            "metadata": {"resourceVersion": "42"},
        }

        result = service.list_workflow_templates()

        assert isinstance(result, WorkflowTemplateList)
        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        assert call_args[0][0] == "get"
        assert call_args[1]["url"] == "https://localhost:2746/api/v1/workflow-templates/argo"

    def test_create_workflow_template(self, service, mock_session):
        """Test the create_workflow_template method."""
        mock_session.request.return_value.json.return_value = {
            "metadata": {"name": "test-template", "namespace": "argo"},
            "spec": {},
        }

        req = WorkflowTemplateCreateRequest(
            template=WorkflowTemplate(metadata={"name": "test-template"}, spec={"entrypoint": "main", "templates": []})
        )
        result = service.create_workflow_template(req)

        assert isinstance(result, WorkflowTemplate)
        assert result.metadata.name == "test-template"
        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        assert call_args[0][0] == "post"
        assert call_args[1]["url"] == "https://localhost:2746/api/v1/workflow-templates/argo"

    def test_list_cluster_workflow_templates(self, service, mock_session):
        """Test the list_cluster_workflow_templates method."""
        mock_session.request.return_value.json.return_value = {
            "items": [],
            "metadata": {"resourceVersion": "42"},
        }

        result = service.list_cluster_workflow_templates()

        assert isinstance(result, ClusterWorkflowTemplateList)
        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        assert call_args[0][0] == "get"
        assert call_args[1]["url"] == "https://localhost:2746/api/v1/cluster-workflow-templates"

    def test_create_cluster_workflow_template(self, service, mock_session):
        """Test the create_cluster_workflow_template method."""
        mock_session.request.return_value.json.return_value = {
            "metadata": {"name": "test-cwt"},
            "spec": {},
        }

        req = ClusterWorkflowTemplateCreateRequest(
            template=ClusterWorkflowTemplate(
                metadata={"name": "test-cwt"}, spec={"entrypoint": "main", "templates": []}
            )
        )
        result = service.create_cluster_workflow_template(req)

        assert isinstance(result, ClusterWorkflowTemplate)
        assert result.metadata.name == "test-cwt"
        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        assert call_args[0][0] == "post"
        assert call_args[1]["url"] == "https://localhost:2746/api/v1/cluster-workflow-templates"

    def test_get_info(self, service, mock_session):
        """Test the get_info method."""
        mock_session.request.return_value.json.return_value = {
            "managedNamespace": "argo",
            "links": [],
        }

        result = service.get_info()

        assert isinstance(result, InfoResponse)
        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        assert call_args[0][0] == "get"
        assert call_args[1]["url"] == "https://localhost:2746/api/v1/info"

    def test_get_workflow_link(self, service):
        """Test the get_workflow_link method."""
        link = service.get_workflow_link("test-workflow")
        assert link == "https://localhost:2746/workflows/argo/test-workflow?tab=workflow"

    def test_get_cron_workflow_link(self, service):
        """Test the get_cron_workflow_link method."""
        link = service.get_cron_workflow_link("test-cron")
        assert link == "https://localhost:2746/cron-workflows/argo/test-cron"

    def test_error_handling(self, service, mock_session):
        """Test error handling in API methods."""
        mock_session.request.return_value.ok = False
        mock_session.request.return_value.status_code = 404
        mock_session.request.return_value.json.return_value = {"message": "Not found"}

        with pytest.raises(NotFound) as excinfo:
            service.get_workflow("non-existent")

        assert "Not found" in str(excinfo.value)
        assert excinfo.value.status_code == 404

    def test_invalid_host_scheme(self):
        """Test that an assertion error is raised for invalid host schemes."""
        service = WorkflowsService(host="localhost:2746")

        with pytest.raises(AssertionError, match="The host scheme is required for service usage"):
            service.list_workflows()
