from hera.shared import global_config
from hera.workflows import Workflow, script
from hera.workflows.artifact import Artifact, HTTPArtifact
from hera.workflows.steps import Steps

global_config.experimental_features["script_annotations"] = True
global_config.experimental_features["script_runner"] = True


@script(
    inputs=[
        HTTPArtifact(
            name="my_artifact",
            path="tmp/file",
            url="https://storage.googleapis.com/kubernetes-release/release/v1.8.0/bin/linux/amd64/kubectl",
            auth={"name": "http-auth", "key": "http-key"},
            headers=[{"name": "header1", "value": "value1"}, {"name": "header2", "value": "value1"}],
        )
    ]
)
def read_artifact(my_artifact) -> str:
    return my_artifact


with Workflow(generate_name="test-types-", entrypoint="my_steps") as w:
    with Steps(name="my_steps") as s:
        read_artifact(arguments=[Artifact(name="my_artifact", from_="somewhere")])
