# Archive-Location

This example showcases how to set an archive location.

https://github.com/argoproj/argo-workflows/blob/master/examples/archive-location.yaml

```python
from hera import ArtifactLocation, Container, Task, Workflow

with Workflow(generate_name="archive-location-") as w:
    Task(
        "whalesay",
        container=Container(image="docker/whalesay:latest", command=["cowsay"], args=["hello", "world"]),
        archive_location=ArtifactLocation(archive_logs=True),
    )

w.create()
```
