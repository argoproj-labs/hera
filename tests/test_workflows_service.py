from pathlib import Path
from unittest.mock import patch

from requests import Session

from hera.workflows.service import WorkflowsService


class TestWorkflowsService:
    def test_token_is_none_when_not_specified(self):
        service = WorkflowsService()
        assert service.token is None

        service = WorkflowsService(token=None)
        assert service.token is None

    def test_adds_bearer_suffix_to_token(self, global_config_fixture):
        global_config_fixture.token = "token"
        service = WorkflowsService()
        assert service.token == "Bearer token"

        global_config_fixture.token = lambda: "lambda-token"
        service = WorkflowsService()
        assert service.token == "Bearer lambda-token"

        service = WorkflowsService(token="token")
        assert service.token == "Bearer token"

    def test_does_not_add_bearer_suffix_if_already_present(self, global_config_fixture):
        global_config_fixture.token = "Bearer token"
        service = WorkflowsService()
        assert service.token == "Bearer token"

        service = WorkflowsService(token="Bearer token")
        assert service.token == "Bearer token"

    def test_adds_custom_token(self):
        service = WorkflowsService(token="something token")
        assert service.token == "something token"

    def test_workflow_client_cert_is_present(self, global_config_fixture):
        random_path = "random_path"
        global_certs_path = "global_certs"

        service = WorkflowsService()
        assert service.client_certs is None

        service = WorkflowsService(client_certs=(random_path, random_path))
        assert service.client_certs == (random_path, random_path)

        assert global_config_fixture.client_certs is None

        global_config_fixture.client_certs = (Path(global_certs_path), Path(global_certs_path))
        assert global_config_fixture.client_certs == (global_certs_path, global_certs_path)

        service = WorkflowsService()
        assert service.client_certs == (global_certs_path, global_certs_path)

        service = WorkflowsService(client_certs=(random_path, random_path))
        assert service.client_certs == (random_path, random_path)

    def test_session_is_none_when_not_specified(self):
        service = WorkflowsService()
        assert service.session is None

        service = WorkflowsService(use_session=False)
        assert service.session is None

    def test_session_is_used_if_set(self):
        service = WorkflowsService(use_session=True)

        assert service.session is not None
        assert isinstance(service.session, Session)

    def test_service_request_no_session(self):
        service = WorkflowsService(host="https://localhost:2746", use_session=False)

        with patch("requests.request") as mock_request, patch("requests.Session.request") as mock_session:
            mock_request.return_value.ok = True
            mock_request.return_value.json.return_value = {"items": [], "metadata": {"resourceVersion": "42"}}
            service.list_workflows("argo")

        mock_request.assert_called_once()
        # requests.request calls the Session request but since we mocked it, it shouldn't have been called
        mock_session.assert_not_called()

    def test_service_request_with_session(self):
        service = WorkflowsService(host="https://localhost:2746", use_session=True)

        with patch("requests.request") as mock_request, patch("requests.Session.request") as mock_session:
            mock_session.return_value.ok = True
            mock_session.return_value.json.return_value = {"items": [], "metadata": {"resourceVersion": "42"}}
            service.list_workflows("argo")

        mock_session.assert_called_once()
        mock_request.assert_not_called()
