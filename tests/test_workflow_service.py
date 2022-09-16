from unittest.mock import Mock

from argo_workflows.api_client import ApiClient

from hera import WorkflowService


def test_ws_has_expected_fields_upon_init():
    ws = WorkflowService(host="https://abc.com", token="abc", verify_ssl=True, namespace="argo")

    assert ws._host == "https://abc.com"
    assert ws._verify_ssl
    assert ws._namespace == "argo"
    assert isinstance(ws._api_client, ApiClient)


def test_ws_get_workflow_link_returns_expected_link():
    mock_service = Mock()
    ws = WorkflowService(host="https://abc.com", token="abc")
    ws.service = mock_service

    link = ws.get_workflow_link("my-wf")
    assert link == "https://abc.com/workflows/default/my-wf?tab=workflow"
