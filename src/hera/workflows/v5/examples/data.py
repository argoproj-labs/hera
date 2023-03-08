from hera.expr import g, it
from hera.workflows import models as m
from hera.workflows.v5.data import Data
from hera.workflows.v5.workflow import Workflow

with Workflow(generate_name="data-") as w:
    Data(
        name="list-log-files",
        artifact_paths=m.ArtifactPaths(name="test-bucket", s3={"bucket": "my-bucket"}),
        transformations=[g.data.filter(it.ends_with("main.log"))],  # type: ignore
        outputs=[m.Artifact(name="file", path="/file")],
    )
