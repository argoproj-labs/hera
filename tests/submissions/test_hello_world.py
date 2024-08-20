import pytest

from hera.workflows import Parameter, Steps, Workflow, WorkflowsService, script
from hera.workflows.models import (
    NodeStatus,
    Parameter as ModelParameter,
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
    ) as w:
        with Steps(name="steps"):
            echo_to_param(arguments={"message": "Hello world!"})
    return w


@pytest.mark.on_cluster
def test_create_hello_world():
    model_workflow = get_workflow().create(wait=True)
    assert model_workflow.status and model_workflow.status.phase == "Succeeded"

    echo_node: NodeStatus = next(
        filter(lambda n: n.display_name == "echo-to-param", model_workflow.status.nodes.values())
    )
    message_out: ModelParameter = next(filter(lambda n: n.name == "message-out", echo_node.outputs.parameters))
    assert message_out.value == "Hello world!"
