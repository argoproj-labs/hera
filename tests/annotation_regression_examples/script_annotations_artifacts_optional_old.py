from hera.workflows import Workflow, script
from hera.workflows.artifact import Artifact
from hera.workflows.steps import Steps


@script(inputs=[Artifact(name="my_artifact", path="tmp/file", optional=True)])
def read_artifact(my_artifact) -> str:
    return my_artifact


with Workflow(generate_name="test-types-", entrypoint="my_steps") as w:
    with Steps(name="my_steps") as s:
        read_artifact(arguments=[Artifact(name="my_artifact", from_="somewhere")])
