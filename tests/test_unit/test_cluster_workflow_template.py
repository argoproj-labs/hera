from unittest.mock import MagicMock

import pytest

from hera.exceptions import NotFound
from hera.workflows.cluster_workflow_template import ClusterWorkflowTemplate
from hera.workflows.models import (
    ClusterWorkflowTemplateCreateRequest,
    ClusterWorkflowTemplateLintRequest,
    ClusterWorkflowTemplateUpdateRequest,
)
from hera.workflows.service import WorkflowsService


def test_cluster_workflow_template_setting_namespace_errors():
    with pytest.raises(ValueError) as e:
        with ClusterWorkflowTemplate(name="my-cwt", namespace="my-namespace"):
            pass

    assert "namespace is not a valid field on a ClusterWorkflowTemplate" in str(e.value)


def test_cluster_workflow_template_create():
    ws = WorkflowsService()
    ws.create_cluster_workflow_template = MagicMock()

    # GIVEN
    with ClusterWorkflowTemplate(
        name="my-cwt",
        workflows_service=ws,
    ) as cwt:
        pass

    # WHEN
    cwt.create()

    # THEN
    built_cwt = cwt.build()
    cwt.workflows_service.create_cluster_workflow_template.assert_called_once_with(
        ClusterWorkflowTemplateCreateRequest(template=built_cwt)
    )


def test_cluster_workflow_template_get():
    # GIVEN
    with ClusterWorkflowTemplate(
        name="my-cwt",
    ) as cwt:
        pass

    ws = WorkflowsService()
    ws.get_cluster_workflow_template = MagicMock(return_value=cwt.build())
    cwt.workflows_service = ws

    # WHEN
    got_cwt = cwt.get()

    # THEN
    cwt.workflows_service.get_cluster_workflow_template.assert_called_once_with(name="my-cwt")
    assert got_cwt == cwt.build()


def test_cluster_workflow_template_lint():
    # GIVEN
    with ClusterWorkflowTemplate(
        name="my-cwt",
    ) as cwt:
        pass

    ws = WorkflowsService()
    ws.lint_cluster_workflow_template = MagicMock(return_value=cwt.build())
    cwt.workflows_service = ws

    # WHEN
    got_cwt = cwt.lint()

    # THEN
    cwt.workflows_service.lint_cluster_workflow_template.assert_called_once_with(
        ClusterWorkflowTemplateLintRequest(template=cwt.build())
    )
    assert got_cwt == cwt.build()


def test_cluster_workflow_template_update_existing_cwt():
    # GIVEN
    with ClusterWorkflowTemplate(
        name="my-cwt",
    ) as cwt:
        pass

    ws = WorkflowsService()
    ws.update_cluster_workflow_template = MagicMock(return_value=cwt.build())
    cwt.workflows_service = ws

    ClusterWorkflowTemplate.get = MagicMock(return_value=cwt.build())

    # WHEN
    got_cwt = cwt.update()

    # THEN
    cwt.get.assert_called_once()
    cwt.workflows_service.update_cluster_workflow_template.assert_called_once_with(
        "my-cwt",
        ClusterWorkflowTemplateUpdateRequest(template=cwt.build()),
    )
    assert got_cwt == cwt.build()


def test_cluster_workflow_template_update_non_existent():
    # GIVEN
    with ClusterWorkflowTemplate(
        name="my-cwt",
    ) as cwt:
        pass

    ws = WorkflowsService()
    ws.create_cluster_workflow_template = MagicMock(return_value=cwt.build())
    ws.update_cluster_workflow_template = MagicMock()  # to ensure NOT called

    cwt.workflows_service = ws

    ClusterWorkflowTemplate.get = MagicMock(side_effect=NotFound())

    # WHEN
    got_cwt = cwt.update()

    # THEN
    assert got_cwt == cwt.build()
    cwt.get.assert_called_once()
    cwt.workflows_service.create_cluster_workflow_template.assert_called_once_with(
        ClusterWorkflowTemplateCreateRequest(template=cwt.build())
    )
    cwt.workflows_service.update_cluster_workflow_template.assert_not_called()
