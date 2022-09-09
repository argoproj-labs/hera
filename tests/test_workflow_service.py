from unittest.mock import Mock

from argo_workflows.api_client import ApiClient
from argo_workflows.apis import WorkflowServiceApi
from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1Workflow,
    IoArgoprojWorkflowV1alpha1WorkflowCreateRequest,
    IoArgoprojWorkflowV1alpha1WorkflowSpec,
    IoArgoprojWorkflowV1alpha1WorkflowStatus,
    ObjectMeta,
)

from hera import WorkflowService, WorkflowStatus


def test_ws_has_expected_fields_upon_init():
    ws = WorkflowService(host="https://abc.com", token="abc", verify_ssl=True, namespace="argo")

    assert ws._host == "https://abc.com"
    assert ws._verify_ssl
    assert ws.namespace == "argo"
    assert isinstance(ws.service, WorkflowServiceApi)
    assert isinstance(ws.service.api_client, ApiClient)


def test_ws_calls_create_as_expected():
    mock_service = Mock()
    mock_service.create_workflow = Mock()

    ws = WorkflowService(host="https://abc.com", token="abc")
    ws.service = mock_service
    w = IoArgoprojWorkflowV1alpha1Workflow(metadata=ObjectMeta(), spec=IoArgoprojWorkflowV1alpha1WorkflowSpec())
    ws.create(w)

    mock_service.create_workflow.assert_called_with(
        "default",
        IoArgoprojWorkflowV1alpha1WorkflowCreateRequest(workflow=w, _check_type=False),
        _check_return_type=False,
    )


def test_ws_calls_delete_as_expected():
    mock_service = Mock()
    mock_service.delete_workflow = Mock()

    ws = WorkflowService(host="https://abc.com", token="abc")
    ws.service = mock_service
    ws.delete("my-wf")

    mock_service.delete_workflow.assert_called_with("default", "my-wf")


def test_ws_get_workflow_link_returns_expected_link():
    mock_service = Mock()
    ws = WorkflowService(host="https://abc.com", token="abc")
    ws.service = mock_service

    link = ws.get_workflow_link("my-wf")
    assert link == "https://abc.com/workflows/default/my-wf?tab=workflow"


def test_ws_get_workflow_returns_expected_workflow():
    mock_service = Mock()
    mock_service.get_workflow = Mock()
    mock_service.get_workflow.return_value = IoArgoprojWorkflowV1alpha1Workflow(
        metadata=ObjectMeta(name="abc"), spec=IoArgoprojWorkflowV1alpha1WorkflowSpec()
    )

    ws = WorkflowService(host="https://abc.com", token="abc")
    ws.service = mock_service

    expected = IoArgoprojWorkflowV1alpha1Workflow(
        metadata=ObjectMeta(name="abc"), spec=IoArgoprojWorkflowV1alpha1WorkflowSpec()
    )
    actual = ws.get_workflow("abc")
    mock_service.get_workflow.assert_called_with("default", "abc", _check_return_type=False)
    assert expected == actual


def test_ws_get_workflow_status_returns_expected_status():
    mock_service = Mock()
    mock_service.get_workflow = Mock()
    mock_service.get_workflow.return_value = IoArgoprojWorkflowV1alpha1Workflow(
        metadata=ObjectMeta(name="abc"),
        spec=IoArgoprojWorkflowV1alpha1WorkflowSpec(),
        status=IoArgoprojWorkflowV1alpha1WorkflowStatus(phase="Succeeded"),
    )

    ws = WorkflowService(host="https://abc.com", token="abc")
    ws.service = mock_service

    expected = WorkflowStatus.Succeeded
    actual = ws.get_workflow_status("abc")
    mock_service.get_workflow.assert_called_with("default", "abc", _check_return_type=False)
    assert expected == actual
