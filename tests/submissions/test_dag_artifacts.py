import pytest

from hera.workflows import DAG, Artifact, Container, NoneArchiveStrategy, Workflow, WorkflowsService


def get_workflow() -> Workflow:
    with Workflow(
        generate_name="dag-artifact-passing-",
        entrypoint="runner-dag",
        namespace="argo",
        workflows_service=WorkflowsService(
            host="https://localhost:2746",
            namespace="argo",
            verify_ssl=False,
        ),
        service_account_name="argo",
    ) as w:
        hello_world_to_file = Container(
            name="hello-world-to-file",
            image="busybox",
            command=["sh", "-c"],
            args=["sleep 1; echo hello world | tee /tmp/hello_world.txt"],
            outputs=[Artifact(name="hello-art", path="/tmp/hello_world.txt", archive=NoneArchiveStrategy())],
        )
        print_message_from_file = Container(
            name="print-message-from-file",
            image="alpine:latest",
            command=["sh", "-c"],
            args=["cat /tmp/message"],
            inputs=[Artifact(name="message", path="/tmp/message")],
        )

        with DAG(
            name="generate-artifact-dag",
            outputs=[Artifact(name="hello-file", from_="{{tasks.hello-world-to-file.outputs.artifacts.hello-art}}")],
        ) as d1:
            hello_world_to_file()

        with DAG(name="consume-artifact-dag", inputs=[Artifact(name="hello-file-input")]) as d2:
            print_message_from_file(
                arguments=d2.get_artifact("hello-file-input").with_name("message"),
            )

        with DAG(name="runner-dag"):
            generator_dag = d1()
            consumer_dag = d2(arguments=generator_dag.get_artifact("hello-file").with_name("hello-file-input"))

            generator_dag >> consumer_dag

    return w


@pytest.mark.xfail(reason="Bucket not created correctly by Minio setup script")
@pytest.mark.on_cluster
def test_dag_artifacts():
    model_workflow = get_workflow().create(wait=True)
    assert model_workflow.status and model_workflow.status.phase == "Succeeded"
