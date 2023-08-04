from hera.workflows import Workflow, script
from hera.workflows.artifact import Artifact, GCSArtifact
from hera.workflows.steps import Steps


@script(
    inputs=[
        GCSArtifact(
            name="my_artifact",
            path="tmp/file",
            bucket="my-bucket-name",
            key="path/in/bucket",
            service_account_key_secret={"name": "my-gcs-credentials", "key": "serviceAccountKey"},
        )
    ]
)
def read_artifact(my_artifact) -> str:
    return my_artifact


with Workflow(generate_name="test-types-", entrypoint="my_steps") as w:
    with Steps(name="my_steps") as s:
        read_artifact(arguments=[Artifact(name="my_artifact", from_="somewhere")])
