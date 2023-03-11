# Coinflip





## Hera

```python
from hera.workflows.container import Container
from hera.workflows.workflow import Workflow

with Workflow(
    generate_name="coinflip-",
    annotations={
        "workflows.argoproj.io/description": (
            "This is an example of coin flip defined as a sequence of conditional steps."
        ),
    },
) as w:
    Container(
        name="heads",
        image="alpine:3.6",
        command=["sh", "-c"],
        args=["echo 'it was heads'"],
    )
    Container(
        name="tails",
        image="alpine:3.6",
        command=["sh", "-c"],
        args=["echo 'it was tails'"],
    )
```

## YAML

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  annotations:
    workflows.argoproj.io/description: This is an example of coin flip defined as
      a sequence of conditional steps.
  generateName: coinflip-
spec:
  templates:
  - container:
      args:
      - echo 'it was heads'
      command:
      - sh
      - -c
      image: alpine:3.6
    name: heads
  - container:
      args:
      - echo 'it was tails'
      command:
      - sh
      - -c
      image: alpine:3.6
    name: tails
```
