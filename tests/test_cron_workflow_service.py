from unittest.mock import Mock

from argo_workflows.api_client import ApiClient
from argo_workflows.apis import CronWorkflowServiceApi
from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1CreateCronWorkflowRequest,
    IoArgoprojWorkflowV1alpha1CronWorkflow,
    IoArgoprojWorkflowV1alpha1CronWorkflowSpec,
    IoArgoprojWorkflowV1alpha1UpdateCronWorkflowRequest,
    IoArgoprojWorkflowV1alpha1WorkflowSpec,
    ObjectMeta,
)

from hera import CronWorkflowService


def test_ws_has_expected_fields_upon_init():
    ws = CronWorkflowService(host="https://abc.com", token="abc", verify_ssl=True, namespace="argo")

    assert ws._host == "https://abc.com"
    assert ws._verify_ssl
    assert ws.namespace == "argo"
    assert isinstance(ws.service, CronWorkflowServiceApi)
    assert isinstance(ws.service.api_client, ApiClient)


def test_ws_calls_create_as_expected():
    mock_service = Mock()
    mock_service.create_cron_workflow = Mock()

    ws = CronWorkflowService(host="https://abc.com", token="abc")
    ws.service = mock_service
    w = IoArgoprojWorkflowV1alpha1CronWorkflow(
        metadata=ObjectMeta(),
        spec=IoArgoprojWorkflowV1alpha1CronWorkflowSpec(
            schedule="* * * * *", workflow_spec=IoArgoprojWorkflowV1alpha1WorkflowSpec()
        ),
    )
    ws.create(w)

    mock_service.create_cron_workflow.assert_called_with(
        "default",
        IoArgoprojWorkflowV1alpha1CreateCronWorkflowRequest(cron_workflow=w, _check_type=False),
        _check_return_type=False,
    )


def test_ws_calls_delete_as_expected():
    mock_service = Mock()
    mock_service.delete_cron_workflow = Mock()

    ws = CronWorkflowService(host="https://abc.com", token="abc")
    ws.service = mock_service
    ws.delete("my-wf")

    mock_service.delete_cron_workflow.assert_called_with("default", "my-wf")


def test_ws_calls_update_as_expected():
    mock_service = Mock()
    mock_service.update_cron_workflow = Mock()

    ws = CronWorkflowService(host="https://abc.com", token="abc")
    ws.service = mock_service
    w = IoArgoprojWorkflowV1alpha1CronWorkflow(
        metadata=ObjectMeta(),
        spec=IoArgoprojWorkflowV1alpha1CronWorkflowSpec(
            schedule="* * * * *", workflow_spec=IoArgoprojWorkflowV1alpha1WorkflowSpec()
        ),
    )
    ws.update("my-wf", w)

    mock_service.update_cron_workflow.assert_called_with(
        "default",
        "my-wf",
        IoArgoprojWorkflowV1alpha1UpdateCronWorkflowRequest(cron_workflow=w, _check_type=False),
        _check_return_type=False,
    )


def test_ws_get_workflow_link_returns_expected_link():
    mock_service = Mock()
    ws = CronWorkflowService(host="https://abc.com", token="abc")
    ws.service = mock_service

    link = ws.get_cron_workflow_link("my-wf")
    assert link == "https://abc.com/cron-workflows/default/my-wf"


def test_ws_get_workflow_returns_expected_workflow():
    mock_service = Mock()
    mock_service.get_cron_workflow = Mock()
    mock_service.get_cron_workflow.return_value = IoArgoprojWorkflowV1alpha1CronWorkflow(
        metadata=ObjectMeta(name="abc"),
        spec=IoArgoprojWorkflowV1alpha1CronWorkflowSpec(
            schedule="* * * * *", workflow_spec=IoArgoprojWorkflowV1alpha1WorkflowSpec()
        ),
    )

    ws = CronWorkflowService(host="https://abc.com", token="abc")
    ws.service = mock_service

    expected = IoArgoprojWorkflowV1alpha1CronWorkflow(
        metadata=ObjectMeta(name="abc"),
        spec=IoArgoprojWorkflowV1alpha1CronWorkflowSpec(
            schedule="* * * * *", workflow_spec=IoArgoprojWorkflowV1alpha1WorkflowSpec()
        ),
    )
    actual = ws.get_workflow("abc")
    mock_service.get_cron_workflow.assert_called_with("default", "abc", _check_return_type=False)
    assert expected == actual
