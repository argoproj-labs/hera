import asyncio
from pathlib import Path
from unittest.mock import MagicMock, patch

from httpx import AsyncClient
from requests import Session

from hera.workflows.async_service import AsyncWorkflowsService
from hera.workflows.service import WorkflowsService


class CustomSession(Session):
    def __init__(self):
        super().__init__()
        self.headers.update({"X-Custom-Header": "FooBar"})


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

    def test_session_is_used(self):
        service = WorkflowsService()

        assert service.session is not None
        assert isinstance(service.session, Session)

    def test_session_is_used_if_custom(self):
        session = CustomSession()
        service = WorkflowsService(session=session)

        assert service.session is not None
        assert isinstance(service.session, CustomSession)

    def test_service_request_with_custom_session(self):
        with patch("requests.request") as mock_request, patch(f"{__name__}.CustomSession.request") as mock_session:
            mock_session.return_value.ok = True
            mock_session.return_value.json.return_value = {"items": [], "metadata": {"resourceVersion": "42"}}

            session = CustomSession()
            with WorkflowsService(host="https://localhost:2746", session=session) as ws:
                ws.list_workflows("argo")

        mock_session.assert_called_once()
        mock_request.assert_not_called()

    def test_service_request_with_session(self):
        service = WorkflowsService(host="https://localhost:2746")

        with patch("requests.request") as mock_request, patch("requests.Session.request") as mock_session:
            mock_session.return_value.ok = True
            mock_session.return_value.json.return_value = {"items": [], "metadata": {"resourceVersion": "42"}}
            service.list_workflows("argo")

        mock_session.assert_called_once()
        mock_request.assert_not_called()

    def test_service_close_session(self):
        with patch("requests.Session.close") as mock_close:
            with WorkflowsService():
                pass

        mock_close.assert_called_once()


class CustomAsyncClient(AsyncClient):
    def __init__(self):
        super().__init__()
        self.headers.update({"X-Custom-Header": "FooBar"})


async def dummy_func():
    await asyncio.sleep(0.3)


class TestAsyncWorkflowsService:
    async def test_dummy(self):
        await dummy_func()

    def test_token_is_none_when_not_specified(self):
        service = AsyncWorkflowsService()
        assert service.token is None

        service = AsyncWorkflowsService(token=None)
        assert service.token is None

    def test_adds_bearer_suffix_to_token(self, global_config_fixture):
        global_config_fixture.token = "token"
        service = AsyncWorkflowsService()
        assert service.token == "Bearer token"

        global_config_fixture.token = lambda: "lambda-token"
        service = AsyncWorkflowsService()
        assert service.token == "Bearer lambda-token"

        service = AsyncWorkflowsService(token="token")
        assert service.token == "Bearer token"

    def test_does_not_add_bearer_suffix_if_already_present(self, global_config_fixture):
        global_config_fixture.token = "Bearer token"
        service = AsyncWorkflowsService()
        assert service.token == "Bearer token"

        service = AsyncWorkflowsService(token="Bearer token")
        assert service.token == "Bearer token"

    def test_adds_custom_token(self):
        service = AsyncWorkflowsService(token="something token")
        assert service.token == "something token"

    def test_workflow_client_cert_is_present(self, global_config_fixture):
        random_path = "random_path"
        global_certs_path = "global_certs"

        with patch("httpx.AsyncClient") as mock_client:
            service = AsyncWorkflowsService()
            assert service.client_certs is None
            mock_client.assert_called_once_with(verify=True, cert=None)

        with patch("httpx.AsyncClient") as mock_client:
            service = AsyncWorkflowsService(client_certs=(random_path, random_path))
            assert service.client_certs == (random_path, random_path)
            mock_client.assert_called_once_with(verify=True, cert=(random_path, random_path))

            assert global_config_fixture.client_certs is None

            global_config_fixture.client_certs = (Path(global_certs_path), Path(global_certs_path))
            assert global_config_fixture.client_certs == (global_certs_path, global_certs_path)

            service = AsyncWorkflowsService()
            assert service.client_certs == (global_certs_path, global_certs_path)

            service = AsyncWorkflowsService(client_certs=(random_path, random_path))
            assert service.client_certs == (random_path, random_path)

    def test_session_is_used(self):
        service = AsyncWorkflowsService()

        assert service.session is not None
        assert isinstance(service.session, AsyncClient)

    def test_session_is_used_if_custom(self):
        session = CustomAsyncClient()
        service = AsyncWorkflowsService(session=session)

        assert service.session is not None
        assert isinstance(service.session, CustomAsyncClient)

    async def test_service_request_with_custom_session(self):
        with patch("httpx.AsyncClient.request") as mock_request, patch(
            f"{__name__}.CustomAsyncClient.request"
        ) as mock_session:
            mock_session.return_value.is_success = True
            mock_session.return_value.json = MagicMock(
                return_value={"items": [], "metadata": {"resourceVersion": "42"}}
            )

            session = CustomAsyncClient()
            async with AsyncWorkflowsService(host="https://localhost:2746", session=session) as ws:
                await ws.list_workflows("argo")

        mock_session.assert_called_once()
        mock_request.assert_not_called()

    async def test_service_request_with_session(self):
        service = AsyncWorkflowsService(host="https://localhost:2746")

        with patch("requests.request") as mock_request, patch("httpx.AsyncClient.request") as mock_session:
            mock_session.return_value.is_success = True
            mock_session.return_value.json = MagicMock(
                return_value={"items": [], "metadata": {"resourceVersion": "42"}}
            )
            await service.list_workflows("argo")

        mock_session.assert_called_once()
        mock_request.assert_not_called()

    async def test_service_close_session(self):
        with patch("httpx.AsyncClient.aclose") as mock_close:
            async with AsyncWorkflowsService():
                pass

        mock_close.assert_called_once()
