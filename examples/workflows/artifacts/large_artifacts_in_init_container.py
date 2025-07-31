"""This example shows how to use `pod_spec_patch` to update the cpu/memory requests for the init container.

This is useful if you want to load a large artifact, but the init container does not have enough memory to load it. This
problem is described in the
[Argo Artifacts Walkthrough](https://argo-workflows.readthedocs.io/en/stable/walk-through/artifacts/).

In Hera, the `resources` field of the template only sets the `main` container resources. We can use a `pod_spec_patch`
to set the init container resources.
"""

import json

from hera.workflows import (
    Artifact,
    NoneArchiveStrategy,
    Resources,
    Steps,
    Workflow,
    script,
)


@script(
    outputs=Artifact(name="out-art", path="/tmp/file", archive=NoneArchiveStrategy()),
    resources=Resources(memory_request="10Ki"),
)
def writer():
    with open("/tmp/file", "w") as f:
        f.write("Hello, world!")


@script(
    inputs=Artifact(name="in-art", path="/tmp/file"),
    resources=Resources(memory_request="10Ki"),
    pod_spec_patch=json.dumps({"initContainers": [{"name": "init", "resources": {"requests": {"memory": "10Ki"}}}]}),
)
def consumer():
    with open("/tmp/file", "r") as f:
        print(f.readlines())  # prints `Hello, world!` to `stdout`


with Workflow(generate_name="artifact-", entrypoint="steps") as w:
    with Steps(name="steps"):
        w_ = writer()
        c = consumer(arguments={"in-art": w_.get_artifact("out-art")})
