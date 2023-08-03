from hera.shared import global_config
from hera.workflows import Workflow, script
from hera.workflows.artifact import Artifact
from hera.workflows.steps import Steps

global_config.experimental_features["script_annotations"] = True
global_config.experimental_features["script_runner"] = True


@script(inputs=[Artifact(name="my_artifact", path="tmp/file", subpath="tmp")])
def read_artifact(my_artifact) -> str:
    return my_artifact


with Workflow(generate_name="test-types-", entrypoint="my_steps") as w:
    with Steps(name="my_steps") as s:
        read_artifact(arguments=[Artifact(name="my_artifact", from_="somewhere")])
