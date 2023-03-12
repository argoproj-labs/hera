# Parallel Workflow





## Hera

```python
from hera.workflows.container_set import ContainerNode, ContainerSet
from hera.workflows.workflow import Workflow

with Workflow(
    generate_name="parallel-",
    entrypoint="main",
    labels={"workflows.argoproj.io/test": "true"},
    annotations={
        "workflows.argoproj.io/description": "This workflow demonstrates running a parallel containers within a single pod.",
        "workflows.argoproj.io/version": ">= 3.1.0",
    },
) as w:
    with ContainerSet(name="main"):
        ContainerNode(name="a", image="argoproj/argosay:v2")
        ContainerNode(name="b", image="argoproj/argosay:v2")
```

## YAML

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  annotations:
    workflows.argoproj.io/description: This workflow demonstrates running a parallel
      containers within a single pod.
    workflows.argoproj.io/version: '>= 3.1.0'
  generateName: parallel-
  labels:
    workflows.argoproj.io/test: 'true'
spec:
  entrypoint: main
  templates:
  - containerSet:
      containers:
      - image: argoproj/argosay:v2
        name: a
      - image: argoproj/argosay:v2
        name: b
    name: main
```
