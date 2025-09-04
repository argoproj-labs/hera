import pytest

from hera.workflows import Parameter, Steps, Workflow, WorkflowsService, script
from hera.workflows.async_service import AsyncWorkflowsService
from hera.workflows.models import (
    NodeStatus,
    Parameter as ModelParameter,
    Workflow as ModelWorkflow,
)


@script(outputs=Parameter(name="message-out", value_from={"path": "/tmp/message-out"}))
def echo_to_param(message: str):
    with open("/tmp/message-out", "w") as f:
        f.write(message)


def get_workflow() -> Workflow:
    with Workflow(
        generate_name="hello-world-",
        entrypoint="steps",
        namespace="argo",
        workflows_service=WorkflowsService(
            host="https://localhost:2746",
            namespace="argo",
            verify_ssl=False,
        ),
        service_account_name="argo",
    ) as w:
        with Steps(name="steps"):
            echo_to_param(arguments={"message": "Hello world!"})
    return w


@pytest.mark.on_cluster
def test_create_hello_world():
    model_workflow = get_workflow().create(wait=True)
    assert isinstance(model_workflow, ModelWorkflow)
    assert model_workflow.status and model_workflow.status.phase == "Succeeded"

    assert model_workflow.status.nodes
    echo_node: NodeStatus = next(
        filter(lambda n: n.display_name == "echo-to-param", model_workflow.status.nodes.values())
    )
    assert echo_node.outputs and echo_node.outputs.parameters
    message_out: ModelParameter = next(filter(lambda n: n.name == "message-out", echo_node.outputs.parameters))
    assert message_out.value == "Hello world!"


@pytest.mark.on_cluster
async def test_async_create_hello_world():
    w = get_workflow()
    w.generate_name = "async-create-hello-world-"
    w.workflows_service = AsyncWorkflowsService(
        host="https://localhost:2746",
        namespace="argo",
        verify_ssl=False,
    )

    model_workflow = await w.async_create(wait=True)
    assert isinstance(model_workflow, ModelWorkflow)
    assert model_workflow.status and model_workflow.status.phase == "Succeeded"

    assert model_workflow.status.nodes
    echo_node: NodeStatus = next(
        filter(lambda n: n.display_name == "echo-to-param", model_workflow.status.nodes.values())
    )
    assert echo_node.outputs and echo_node.outputs.parameters
    message_out: ModelParameter = next(filter(lambda n: n.name == "message-out", echo_node.outputs.parameters))
    assert message_out.value == "Hello world!"
