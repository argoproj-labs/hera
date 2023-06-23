from unittest.mock import MagicMock, patch

import pytest

from hera.exceptions import NotFound
from hera.shared import global_config
from hera.workflows import Container, Steps
from hera.workflows.models import (
    WorkflowCreateRequest,
    WorkflowStatus,
    WorkflowTemplateCreateRequest,
    WorkflowTemplateLintRequest,
    WorkflowTemplateUpdateRequest,
)
from hera.workflows.service import WorkflowsService
from hera.workflows.workflow import NAME_LIMIT, Workflow
from hera.workflows.workflow_template import _TRUNCATE_LENGTH, WorkflowTemplate


def test_workflow_template_setting_status_errors():
    with pytest.raises(ValueError) as e:
        with WorkflowTemplate(name="my-wt", namespace="my-namespace", status=WorkflowStatus()):
            pass

    assert "status is not a valid field on a WorkflowTemplate" in str(e.value)


def test_workflow_template_create():
    global_config.host = "http://hera.testing"
    ws = WorkflowsService()
    ws.create_workflow_template = MagicMock()

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


def test_workflow_template_create_as_workflow():
    with patch.object(WorkflowsService, "create_workflow", return_value=MagicMock()) as create_workflow:
        # We have to patch the function at the class level because create_as_workflow copies the workflows service
        # from the WorkflowTemplate to the *separate* Workflow object.

        ws = WorkflowsService(namespace="my-namespace")
        # Note we set the name to None here, otherwise the workflow will take the name from the returned object
        create_workflow.return_value.metadata.name = None

        # GIVEN
        with WorkflowTemplate(
            name="my-wt",
            namespace="my-namespace",
            workflows_service=ws,
        ) as wt:
            cowsay = Container(name="cowsay", image="docker/whalesay", command=["cowsay", "foo"])
            with Steps(name="steps"):
                cowsay()

        expected_workflow = Workflow.from_dict(wt.to_dict())
        expected_workflow.kind = "Workflow"
        expected_workflow.generate_name = expected_workflow.name
        expected_workflow.name = None

        # WHEN
        wt.create_as_workflow()

        # THEN
        wt.workflows_service.create_workflow.assert_called_once_with(
            WorkflowCreateRequest(workflow=expected_workflow.build()),
            namespace="my-namespace",
        )


def test_workflow_template_get_as_workflow():
    # GIVEN
    with WorkflowTemplate(
        name="my-wt",
        namespace="my-namespace",
    ) as wt:
        pass

    # WHEN
    workflow = wt._get_as_workflow(None)

    # THEN
    assert isinstance(workflow, Workflow)
    assert workflow.kind == "Workflow"
    assert workflow.name is None
    assert workflow.generate_name == "my-wt"


def test_workflow_template_get_as_workflow_truncator():
    # GIVEN
    with WorkflowTemplate(
        name="a" * NAME_LIMIT,  # this is a valid WT name, but must be truncated to create a workflow from it
        namespace="my-namespace",
    ) as wt:
        pass

    # WHEN
    workflow = wt._get_as_workflow(None)

    # THEN
    assert isinstance(workflow, Workflow)
    assert workflow.kind == "Workflow"
    assert workflow.name is None
    assert workflow.generate_name == ("a" * _TRUNCATE_LENGTH)


def test_workflow_template_get_as_workflow_with_generate_name():
    # GIVEN
    with WorkflowTemplate(
        name="my-wt",
        namespace="my-namespace",
    ) as wt:
        pass

    # WHEN
    workflow = wt._get_as_workflow(generate_name="my-workflow-")

    # THEN
    assert isinstance(workflow, Workflow)
    assert workflow.kind == "Workflow"
    assert workflow.name is None
    assert workflow.generate_name == "my-workflow-"


def test_workflow_template_get():
    # GIVEN
    with WorkflowTemplate(
        name="my-wt",
        namespace="my-namespace",
    ) as wt:
        pass

    ws = WorkflowsService()
    ws.get_workflow_template = MagicMock(return_value=wt.build())
    wt.workflows_service = ws

    # WHEN
    got_wt = wt.get()

    # THEN
    wt.workflows_service.get_workflow_template.assert_called_once_with(name="my-wt", namespace="my-namespace")
    assert got_wt == wt.build()


def test_workflow_template_lint():
    # GIVEN
    with WorkflowTemplate(
        name="my-wt",
        namespace="my-namespace",
    ) as wt:
        pass

    ws = WorkflowsService()
    ws.lint_workflow_template = MagicMock(return_value=wt.build())
    wt.workflows_service = ws

    # WHEN
    got_wt = wt.lint()

    # THEN
    wt.workflows_service.lint_workflow_template.assert_called_once_with(
        WorkflowTemplateLintRequest(template=wt.build()), namespace="my-namespace"
    )
    assert got_wt == wt.build()


def test_workflow_template_update_existing_wt():
    # GIVEN
    with WorkflowTemplate(
        name="my-wt",
        namespace="my-namespace",
    ) as wt:
        pass

    ws = WorkflowsService()
    ws.update_workflow_template = MagicMock(return_value=wt.build())
    wt.workflows_service = ws

    WorkflowTemplate.get = MagicMock(return_value=wt.build())

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


def test_workflow_template_update_non_existent():
    # GIVEN
    with WorkflowTemplate(
        name="my-wt",
        namespace="my-namespace",
    ) as wt:
        pass

    ws = WorkflowsService()
    ws.create_workflow_template = MagicMock(return_value=wt.build())
    ws.update_workflow_template = MagicMock()  # to ensure NOT called

    wt.workflows_service = ws

    WorkflowTemplate.get = MagicMock(side_effect=NotFound())

    # WHEN
    got_wt = wt.update()

    # THEN
    assert got_wt == wt.build()
    wt.get.assert_called_once()
    wt.workflows_service.create_workflow_template.assert_called_once_with(
        WorkflowTemplateCreateRequest(template=wt.build()), namespace="my-namespace"
    )
    wt.workflows_service.update_workflow_template.assert_not_called()
