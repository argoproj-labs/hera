from unittest.mock import MagicMock

import pytest

from hera.exceptions import NotFound
from hera.workflows.cron_workflow import CronWorkflow
from hera.workflows.models import CreateCronWorkflowRequest, UpdateCronWorkflowRequest
from hera.workflows.service import WorkflowsService


def test_cron_workflow_update_existing_cw():
    # GIVEN
    with CronWorkflow(
        name="my-cw",
        namespace="my-namespace",
        schedule="* * * * *",
    ) as cw:
        pass

    ws = WorkflowsService()
    ws.update_cron_workflow = MagicMock(return_value=cw.build())
    cw.workflows_service = ws

    CronWorkflow.get = MagicMock(return_value=cw.build())

    # WHEN
    got_cw = cw.update()

    # THEN
    cw.get.assert_called_once()
    cw.workflows_service.update_cron_workflow.assert_called_once_with(
        "my-cw",
        UpdateCronWorkflowRequest(cron_workflow=cw.build()),
        namespace="my-namespace",
    )
    assert got_cw == cw.build()


def test_cron_workflow_update_non_existent():
    # GIVEN
    with CronWorkflow(
        name="my-cw",
        namespace="my-namespace",
        schedule="* * * * *",
    ) as cw:
        pass

    ws = WorkflowsService()
    ws.create_cron_workflow = MagicMock(return_value=cw.build())
    ws.update_cron_workflow = MagicMock()  # to ensure NOT called

    cw.workflows_service = ws

    CronWorkflow.get = MagicMock(side_effect=NotFound())

    # WHEN
    got_cw = cw.update()

    # THEN
    assert got_cw == cw.build()
    cw.get.assert_called_once()
    cw.workflows_service.create_cron_workflow.assert_called_once_with(
        CreateCronWorkflowRequest(cron_workflow=cw.build()), namespace="my-namespace"
    )
    cw.workflows_service.update_cron_workflow.assert_not_called()


def test_returns_expected_workflow_link():
    with pytest.raises(AssertionError) as e:
        cw = CronWorkflow(name="test", schedule="* * * * *")
        cw.workflows_service = None
        cw.get_workflow_link()
    assert str(e.value) == "Cannot fetch a cron workflow link without a service"

    with pytest.raises(AssertionError) as e:
        CronWorkflow(
            schedule="* * * * *", workflows_service=WorkflowsService(host="hera.test", namespace="my-namespace")
        ).get_workflow_link()
    assert str(e.value) == "Cannot fetch a cron workflow link without a cron workflow name"

    w = CronWorkflow(
        name="test",
        schedule="* * * * *",
        workflows_service=WorkflowsService(host="hera.test", namespace="my-namespace"),
    )
    assert w.get_workflow_link() == "hera.test/cron-workflows/my-namespace/test"

    w = CronWorkflow(
        name="test",
        schedule="* * * * *",
        workflows_service=WorkflowsService(host="https://localhost:8443/argo/", namespace="my-namespace"),
    )
    assert w.get_workflow_link() == "https://localhost:8443/argo/cron-workflows/my-namespace/test"
