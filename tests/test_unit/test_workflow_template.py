import pytest

from hera.exceptions import NotFound
from hera.workflows.models import (
    WorkflowStatus,
    WorkflowTemplateCreateRequest,
    WorkflowTemplateLintRequest,
    WorkflowTemplateUpdateRequest,
)
from hera.workflows.service import WorkflowsService
from hera.workflows.workflow import Workflow
from hera.workflows.workflow_template import WorkflowTemplate


def test_workflow_template_setting_status_errors():
    with pytest.raises(ValueError) as e:
        with WorkflowTemplate(name="my-wt", namespace="my-namespace", status=WorkflowStatus()):
            pass

    assert "status is not a valid field on a WorkflowTemplate" in str(e.value)


def test_workflow_template_create(mocker):
    ws = WorkflowsService()
    ws.create_workflow_template = mocker.MagicMock()

    # GIVEN
    with WorkflowTemplate(
        name="my-wt",
        namespace="my-namespace",
        workflows_service=ws,
    ) as wt:
        pass

    # WHEN
    wt.create()

    # THEN
    built_wt = wt.build()
    wt.workflows_service.create_workflow_template.assert_called_once_with(
        WorkflowTemplateCreateRequest(template=built_wt), namespace="my-namespace"
    )


def test_workflow_template_create_as_workflow(mocker):
    Workflow.create = mocker.MagicMock()

    # GIVEN
    with WorkflowTemplate(
        name="my-wt",
        namespace="my-namespace",
        workflows_service=WorkflowsService(),
    ) as wt:
        pass

    # WHEN
    wt.create_as_workflow()

    # THEN
    Workflow.create.assert_called_once_with(wait=False, poll_interval=5)


def test_workflow_template_get(mocker):
    # GIVEN
    with WorkflowTemplate(
        name="my-wt",
        namespace="my-namespace",
    ) as wt:
        pass

    ws = WorkflowsService()
    ws.get_workflow_template = mocker.MagicMock(return_value=wt.build())
    wt.workflows_service = ws

    # WHEN
    got_wt = wt.get()

    # THEN
    wt.workflows_service.get_workflow_template.assert_called_once_with(name="my-wt", namespace="my-namespace")
    assert got_wt == wt.build()


def test_workflow_template_lint(mocker):
    # GIVEN
    with WorkflowTemplate(
        name="my-wt",
        namespace="my-namespace",
    ) as wt:
        pass

    ws = WorkflowsService()
    ws.lint_workflow_template = mocker.MagicMock(return_value=wt.build())
    wt.workflows_service = ws

    # WHEN
    got_wt = wt.lint()

    # THEN
    wt.workflows_service.lint_workflow_template.assert_called_once_with(
        WorkflowTemplateLintRequest(template=wt.build()), namespace="my-namespace"
    )
    assert got_wt == wt.build()


def test_workflow_template_update_existing_wt(mocker):
    # GIVEN
    with WorkflowTemplate(
        name="my-wt",
        namespace="my-namespace",
    ) as wt:
        pass

    ws = WorkflowsService()
    ws.update_workflow_template = mocker.MagicMock(return_value=wt.build())
    wt.workflows_service = ws

    WorkflowTemplate.get = mocker.MagicMock(return_value=wt.build())

    # WHEN
    got_wt = wt.update()

    # THEN
    wt.get.assert_called_once()
    wt.workflows_service.update_workflow_template.assert_called_once_with(
        "my-wt",
        WorkflowTemplateUpdateRequest(template=wt.build()),
        namespace="my-namespace",
    )
    assert got_wt == wt.build()


def test_workflow_template_update_non_existent(mocker):
    # GIVEN
    with WorkflowTemplate(
        name="my-wt",
        namespace="my-namespace",
    ) as wt:
        pass

    ws = WorkflowsService()
    ws.create_workflow_template = mocker.MagicMock(return_value=wt.build())
    ws.update_workflow_template = mocker.MagicMock()  # to ensure NOT called

    wt.workflows_service = ws

    WorkflowTemplate.get = mocker.MagicMock(side_effect=NotFound())

    # WHEN
    got_wt = wt.update()

    # THEN
    assert got_wt == wt.build()
    wt.get.assert_called_once()
    wt.workflows_service.create_workflow_template.assert_called_once_with(
        WorkflowTemplateCreateRequest(template=wt.build()), namespace="my-namespace"
    )
    wt.workflows_service.update_workflow_template.assert_not_called()
