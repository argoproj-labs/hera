# Graph Workflow





## Hera

```python
from hera.workflows.container_set import ContainerNode, ContainerSet
from hera.workflows.workflow import Workflow

with Workflow(
    generate_name="graph-",
    entrypoint="main",
    labels={"workflows.argoproj.io/test": "true"},
    annotations={
        "workflows.argoproj.io/description": "This workflow demonstrates running a graph of tasks within containers in a single pod.",
        "workflows.argoproj.io/version": ">= 3.1.0",
    },
) as w:
    with ContainerSet(name="main"):
        a = ContainerNode(name="a", image="argoproj/argosay:v2")
        b = ContainerNode(name="b", image="argoproj/argosay:v2")
        c = ContainerNode(name="c", image="argoproj/argosay:v2")
        d = ContainerNode(name="d", image="argoproj/argosay:v2")
        a >> [b, c] >> d
```

## YAML

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  annotations:
    workflows.argoproj.io/description: This workflow demonstrates running a graph
      of tasks within containers in a single pod.
    workflows.argoproj.io/version: '>= 3.1.0'
  generateName: graph-
  labels:
    workflows.argoproj.io/test: 'true'
spec:
  entrypoint: main
  templates:
  - containerSet:
      containers:
      - image: argoproj/argosay:v2
        name: a
      - dependencies:
        - a
        image: argoproj/argosay:v2
        name: b
      - dependencies:
        - a
        image: argoproj/argosay:v2
        name: c
      - dependencies:
        - b
        - c
        image: argoproj/argosay:v2
        name: d
    name: main
```
