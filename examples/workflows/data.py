from hera.expr import g, it
from hera.workflows import (
    Data,
    Workflow,
    models as m,
)

with Workflow(generate_name="data-") as w:
    Data(
        name="list-log-files",
        artifact_paths=m.ArtifactPaths(name="test-bucket", s3={"bucket": "my-bucket"}),
        transformations=[g.data.filter(it.ends_with("main.log"))],  # type: ignore
        outputs=[m.Artifact(name="file", path="/file")],
    )
