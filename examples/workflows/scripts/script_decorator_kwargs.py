"""This example shows various kwarg parameters for the script decorator."""

from hera.workflows import Resources, Workflow, script
from hera.workflows.models import ImagePullPolicy


@script(
    image_pull_policy=ImagePullPolicy.always,
    resources=Resources(memory_request="5Gi"),
    annotations={"my-annotation": "my-value"},
    labels={"my-label": "my-value"},
)
def script_with_kwargs():
    print("ok")


with Workflow(generate_name="script-with-kwargs-", entrypoint="script-with-kwargs") as w:
    script_with_kwargs()
