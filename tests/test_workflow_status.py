import pytest

from hera import WorkflowStatus


def test_workflow_status_instantiates_as_expected():
    argo_status = 'Running'
    hera_status = WorkflowStatus.from_argo_status(argo_status)

    assert isinstance(hera_status, WorkflowStatus)
    assert hera_status == WorkflowStatus.Running


def test_workflow_status_raises_key_error_on_unrecognized_status():
    argo_status = 'Unknown'

    with pytest.raises(KeyError) as e:
        WorkflowStatus.from_argo_status(argo_status)

    assert f"Unrecognized status {argo_status}" in str(e.value)
