from hera.shared import global_config
from hera.workflows import Workflow, script
from hera.workflows.artifact import Artifact, ArtifactoryArtifact
from hera.workflows.steps import Steps

global_config.experimental_features["script_annotations"] = True
global_config.experimental_features["script_runner"] = True


@script(
    inputs=[
        ArtifactoryArtifact(
            name="my_artifact",
            path="tmp/file",
            url="http://artifactory:8081/artifactory/generic-local/hello_world.tgz",
            password_secret={"name": "my-artifactory-credentials", "key": "secretPassword"},
            username_secret={"name": "my-artifactory-credentials", "key": "secretUsername"},
        )
    ]
)
def read_artifact(my_artifact) -> str:
    return my_artifact


with Workflow(generate_name="test-types-", entrypoint="my_steps") as w:
    with Steps(name="my_steps") as s:
        read_artifact(arguments=[Artifact(name="my_artifact", from_="somewhere")])
