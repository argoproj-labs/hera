# Artifact Gc Workflow

> Note: This example is a replication of an Argo Workflow example in Hera. The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/artifact-gc-workflow.yaml).



## Hera

```python
from hera.workflows import (
    Container,
    S3Artifact,
    Workflow,
    models as m,
)

with Workflow(
    generate_name="artifact-gc-", entrypoint="main", artifact_gc=m.ArtifactGC(strategy="OnWorkflowDeletion")
) as w:
    main = Container(
        name="main",
        image="argoproj/argosay:v2",
        command=["sh", "-c"],
        args=['echo "hello world" > /tmp/on-completion.txt\necho "hello world" > /tmp/on-deletion.txt\n'],
        outputs=[
            S3Artifact(
                name="on-completion",
                path="/tmp/on-completion.txt",
                key="on-completion.txt",
                artifact_gc=m.ArtifactGC(strategy="OnWorkflowCompletion"),
            ),
            S3Artifact(
                name="on-deletion",
                path="/tmp/on-deletion.txt",
                key="on-deletion.txt",
            ),
        ],
    )
```

## YAML

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: artifact-gc-
  namespace: default
spec:
  artifactGC:
    strategy: OnWorkflowDeletion
  entrypoint: main
  templates:
  - container:
      args:
      - 'echo "hello world" > /tmp/on-completion.txt

        echo "hello world" > /tmp/on-deletion.txt

        '
      command:
      - sh
      - -c
      image: argoproj/argosay:v2
    name: main
    outputs:
      artifacts:
      - artifactGC:
          strategy: OnWorkflowCompletion
        name: on-completion
        path: /tmp/on-completion.txt
        s3:
          key: on-completion.txt
      - name: on-deletion
        path: /tmp/on-deletion.txt
        s3:
          key: on-deletion.txt
```
