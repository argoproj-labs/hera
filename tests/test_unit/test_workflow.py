from unittest.mock import MagicMock

import pytest

from hera.workflows.models import WorkflowCreateRequest
from hera.workflows.service import WorkflowsService
from hera.workflows.workflow import NAME_LIMIT, Workflow


def test_workflow_name_validators():
    with pytest.raises(ValueError) as e:
        Workflow(name=("a" * NAME_LIMIT) + "a")

    assert f"name must be no more than {NAME_LIMIT} characters" in str(e.value)

    with pytest.raises(ValueError) as e:
        Workflow(generate_name=("a" * NAME_LIMIT) + "a")

    assert f"name must be no more than {NAME_LIMIT} characters" in str(e.value)


def test_workflow_create():
    ws = WorkflowsService(namespace="my-namespace")
    ws.create_workflow = MagicMock()

    # Note we set the name to None here, otherwise the workflow will take the name from the returned object
    ws.create_workflow.return_value.metadata.name = None

    # GIVEN
    with Workflow(
        generate_name="w",
        namespace="my-namespace",
        workflows_service=ws,
    ) as w:
        pass

    # WHEN
    w.create()

    # THEN
    built_workflow = w.build()
    w.workflows_service.create_workflow.assert_called_once_with(
        WorkflowCreateRequest(workflow=built_workflow), namespace="my-namespace"
    )
