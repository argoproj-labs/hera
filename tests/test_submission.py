import pytest

from hera.workflows import Steps, Workflow, WorkflowsService, script


@script()
def echo(message: str):
    print(message)


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


@pytest.mark.workflow
def test_create_hello_world():
    model_workflow = w.create(wait=True)
    assert model_workflow.status and model_workflow.status.phase == "Succeeded"
