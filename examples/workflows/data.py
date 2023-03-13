from hera.expr import g, it
from hera.workflows import (
    Artifact,
    Data,
    S3Artifact,
    Workflow,
)

with Workflow(generate_name="data-") as w:
    Data(
        name="list-log-files",
        source=S3Artifact(name="test-bucket", bucket="my-bucket"),
        transformations=[g.data.filter(it.ends_with("main.log"))],  # type: ignore
        outputs=[Artifact(name="file", path="/file")],
    )
