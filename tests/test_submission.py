import pytest

from hera.workflows import Steps, Workflow, WorkflowsService, script


@script()
def echo(message: str):
    print(message)


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
            echo(arguments={"message": "Hello world!"})
    return w


@pytest.mark.on_cluster
def test_create_hello_world():
    model_workflow = get_workflow().create(wait=True)
    assert model_workflow.status and model_workflow.status.phase == "Succeeded"

    echo_node = next(filter(lambda n: n.display_name == "echo", model_workflow.status.nodes.values()))
    assert echo_node.outputs.result == "Hello world!"
