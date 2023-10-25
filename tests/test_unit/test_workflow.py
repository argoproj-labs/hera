import importlib
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from hera.workflows.container import Container
from hera.workflows.exceptions import InvalidTemplateCall
from hera.workflows.models import WorkflowCreateRequest
from hera.workflows.parameter import Parameter
from hera.workflows.script import script
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


def test_workflow_to_file(tmp_path: Path):
    # GIVEN
    workflow = importlib.import_module("examples.workflows.coinflip").w

    # WHEN
    yaml_path = workflow.to_file(tmp_path)

    # THEN
    assert yaml_path.exists()
    assert workflow == Workflow.from_file(yaml_path)


def test_workflow_from_yaml():
    # GIVEN
    workflow = importlib.import_module("examples.workflows.coinflip").w

    # THEN
    assert workflow == Workflow.from_yaml(workflow.to_yaml())


@script()
def hello():
    print("hello")


def test_workflow_callable_return_is_none():
    # GIVEN
    with Workflow(name="w"):
        returned_from_script = hello()

    # THEN
    assert returned_from_script is None


def test_workflow_callable_container_raises_error():
    with pytest.raises(InvalidTemplateCall) as e:
        # GIVEN
        with Workflow(name="w"):
            whalesay = Container(
                name="whalesay",
                inputs=[Parameter(name="message")],
                image="docker/whalesay",
                command=["cowsay"],
                args=["{{inputs.parameters.message}}"],
            )

            # WHEN
            whalesay()

    # THEN InvalidTemplateCall raised
    assert "Callable Template 'whalesay' is not callable under a Workflow" in str(e.value)


def test_returns_expected_workflow_link():
    with pytest.raises(AssertionError) as e:
        w = Workflow(name="test")
        w.workflows_service = None
        w.get_workflow_link()
    assert str(e.value) == "Cannot fetch a workflow link without a service"

    with pytest.raises(AssertionError) as e:
        Workflow(workflows_service=WorkflowsService(host="hera.test", namespace="my-namespace")).get_workflow_link()
    assert str(e.value) == "Cannot fetch a workflow link without a workflow name"

    w = Workflow(name="test", workflows_service=WorkflowsService(host="hera.test", namespace="my-namespace"))
    assert w.get_workflow_link() == "hera.test/workflows/my-namespace/test?tab=workflow"
