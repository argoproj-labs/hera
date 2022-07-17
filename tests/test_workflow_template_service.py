from unittest.mock import Mock

from argo_workflows.api_client import ApiClient
from argo_workflows.apis import WorkflowTemplateServiceApi
from argo_workflows.models import (
    IoArgoprojWorkflowV1alpha1WorkflowSpec,
    IoArgoprojWorkflowV1alpha1WorkflowTemplate,
    IoArgoprojWorkflowV1alpha1WorkflowTemplateCreateRequest,
    ObjectMeta,
)

from hera import WorkflowTemplateService


def test_ws_has_expected_fields_upon_init():
    ws = WorkflowTemplateService(host="https://abc.com", token="abc", verify_ssl=True, namespace="argo")

    assert ws._host == "https://abc.com"
    assert ws._verify_ssl
    assert ws.namespace == "argo"
    assert isinstance(ws.service, WorkflowTemplateServiceApi)
    assert isinstance(ws.service.api_client, ApiClient)


def test_ws_calls_create_as_expected():
    mock_service = Mock()
    mock_service.create_workflow_template = Mock()

    ws = WorkflowTemplateService(host="https://abc.com", token="abc")
    ws.service = mock_service
    t = IoArgoprojWorkflowV1alpha1WorkflowTemplate(
        metadata=ObjectMeta(), spec=IoArgoprojWorkflowV1alpha1WorkflowSpec()
    )
    ws.create(t)

    mock_service.create_workflow_template.assert_called_with(
        "default",
        IoArgoprojWorkflowV1alpha1WorkflowTemplateCreateRequest(template=t, _check_type=False),
        _check_return_type=False,
    )


def test_ws_calls_delete_as_expected():
    mock_service = Mock()
    mock_service.delete_workflow_template = Mock()

    ws = WorkflowTemplateService(host="https://abc.com", token="abc")
    ws.service = mock_service
    ws.delete("my-wf")

    mock_service.delete_workflow_template.assert_called_with("default", "my-wf")
