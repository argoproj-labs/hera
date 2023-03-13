# Input Artifact Http

> Note: This example is a replication of an Argo Workflow example in Hera. The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/input-artifact-http.yaml).



## Hera

```python
from hera.workflows import Container, HTTPArtifact, Workflow

with Workflow(generate_name="input-artifact-http-", entrypoint="http-artifact-example") as w:
    Container(
        name="http-artifact-example",
        image="debian:9.4",
        command=["sh", "-c"],
        args=["kubectl version"],
        inputs=[
            HTTPArtifact(
                name="kubectl",
                path="/bin/kubectl",
                mode=493,
                url="https://storage.googleapis.com/kubernetes-release/release/v1.8.0/bin/linux/amd64/kubectl",
            ),
        ],
    )
```

## YAML

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: input-artifact-http-
spec:
  entrypoint: http-artifact-example
  templates:
  - container:
      args:
      - kubectl version
      command:
      - sh
      - -c
      image: debian:9.4
    inputs:
      artifacts:
      - http:
          url: https://storage.googleapis.com/kubernetes-release/release/v1.8.0/bin/linux/amd64/kubectl
        mode: 493
        name: kubectl
        path: /bin/kubectl
    name: http-artifact-example
```
