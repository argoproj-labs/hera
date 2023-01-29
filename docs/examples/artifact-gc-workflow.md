# Artifact-Gc-Workflow

This example showcases how to output artifacts and set the garbage collection property for artifacts

https://github.com/argoproj/argo-workflows/blob/master/examples/artifact-gc-workflow.yaml

```python
from hera import Artifact, ArtifactGC, Container, GCStrategy, S3Artifact, Task, Workflow

with Workflow(
    generate_name="artifact-gc-", artifact_gc=ArtifactGC(strategy=GCStrategy.on_workflow_deletion.value)
) as w:
    Task(
        name="main",
        container=Container(
            image="argoproj/argosay:v2",
            args=["|", 'echo "hello world" > /tmp/on-completion.txt', 'echo "hello world" > /tmp/on-deletion.txt'],
        ),
        outputs=[
            Artifact(
                name="on-completion",
                path="/tmp/on-completion.txt",
                s3=S3Artifact(key="on-completion.txt"),
                artifact_gc=ArtifactGC(strategy=GCStrategy.on_workflow_completion.value),
            ),
            Artifact(name="on-deletion", path="/tmp/on-deletion.txt", s3=S3Artifact(key="on-deletion.txt")),
        ],
    )

w.create()
```
