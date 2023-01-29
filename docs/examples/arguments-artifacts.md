# Arguments-Artifacts

This example showcases how to pass artifacts to a template.

https://github.com/argoproj/argo-workflows/blob/master/examples/arguments-artifacts.yaml

```python
from hera import Artifact, Container, HTTPArtifact, Task, Workflow

with Workflow(
    generate_name="arguments-artifacts-",
    inputs=[
        Artifact(
            name="kubectl",
            http=HTTPArtifact(
                url="https://storage.googleapis.com/kubernetes-release/release/v1.8.0/bin/linux/amd64/kubectl"
            ),
        )
    ],
) as w:
    Task(
        "kubectl-input-artifact",
        inputs=[Artifact(name="kubectl", path="/usr/local/bin/kubectl", mode=755)],
        container=Container(image="debian:9.4", command=["sh", "-c"], args=["kubectl", "version"]),
    )

w.create()
```
