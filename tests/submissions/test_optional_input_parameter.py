from typing import Optional

import pytest

from hera.workflows import Parameter, Steps, Workflow, WorkflowsService, script
from hera.workflows.models import (
    NodeStatus,
    Parameter as ModelParameter,
)


@script(outputs=Parameter(name="message-out", value_from={"path": "/tmp/message-out"}))
def print_msg(message: Optional[str] = None):
    with open("/tmp/message-out", "w") as f:
        f.write("Got: {}".format(message))


def get_workflow() -> Workflow:
    with Workflow(
        generate_name="optional-param-",
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
            print_msg(name="step-1", arguments={"message": "Hello world!"})
            print_msg(name="step-2", arguments={})
            print_msg(name="step-3")

    return w


@pytest.mark.on_cluster
def test_create_workflow_with_optional_input_parameter():
    model_workflow = get_workflow().create(wait=True)
    assert model_workflow.status and model_workflow.status.phase == "Succeeded"

    step_and_expected_output = {
        "step-1": "Got: Hello world!",
        "step-2": "Got: None",
        "step-3": "Got: None",
    }

    for step, expected_output in step_and_expected_output.items():
        node: NodeStatus = next(filter(lambda n: n.display_name == step, model_workflow.status.nodes.values()))
        message_out: ModelParameter = next(filter(lambda n: n.name == "message-out", node.outputs.parameters))
        assert message_out.value == expected_output
