# Workspace Workflow





## Hera

```python
from hera.workflows.container_set import ContainerNode, ContainerSet
from hera.workflows.models import Artifact, ValueFrom, VolumeMount
from hera.workflows.parameter import Parameter
from hera.workflows.volume import EmptyDirVolume
from hera.workflows.workflow import Workflow

with Workflow(
    generate_name="workspace-",
    labels={"workflows.argoproj.io/test": "true"},
    annotations={
        "workflows.argoproj.io/description": "This workflow demonstrates using a workspace to share files between containers. "
        'This also allows containers not called "main" to create output artifacts.',
        "workflows.argoproj.io/version": ">= 3.1.0",
    },
) as w:
    with ContainerSet(
        name="main",
        volumes=[EmptyDirVolume(name="workspace", mount_path="/workspace")],
        volume_mounts=[VolumeMount(name="workspace", mount_path="/workspace")],
        outputs=[
            Parameter(name="out", value_from=ValueFrom(path="/workspace/out")),
            Artifact(name="out", path="/workspace/out"),
        ],
    ):
        ContainerNode(
            name="a",
            image="argoproj/argosay:v2",
            args=["echo", "hi", "/workspace/out"],
        ),
        ContainerNode(
            name="main",
            image="argoproj/argosay:v2",
        ),
```

## YAML

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  annotations:
    workflows.argoproj.io/description: This workflow demonstrates using a workspace
      to share files between containers. This also allows containers not called "main"
      to create output artifacts.
    workflows.argoproj.io/version: '>= 3.1.0'
  generateName: workspace-
  labels:
    workflows.argoproj.io/test: 'true'
spec:
  templates:
  - containerSet:
      containers:
      - args:
        - echo
        - hi
        - /workspace/out
        image: argoproj/argosay:v2
        name: a
      - image: argoproj/argosay:v2
        name: main
      volumeMounts:
      - mountPath: /workspace
        name: workspace
    name: main
    outputs:
      artifacts:
      - name: out
        path: /workspace/out
      parameters:
      - name: out
        valueFrom:
          path: /workspace/out
    volumes:
    - emptyDir: {}
      name: workspace
```
