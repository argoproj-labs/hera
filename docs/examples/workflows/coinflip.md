# Coinflip





## Hera

```python
from hera.workflows import DAG, Workflow, script


@script()
def flip():
    import random

    result = "heads" if random.randint(0, 1) == 0 else "tails"
    print(result)


@script()
def heads():
    print("it was heads")


@script()
def tails():
    print("it was tails")


with Workflow(generate_name="coinflip-", entrypoint="d") as w:
    with DAG(name="d") as s:
        f = flip()
        heads().on_other_result(f, "heads")
        tails().on_other_result(f, "tails")
```

## YAML

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: coinflip-
spec:
  entrypoint: d
  templates:
  - dag:
      tasks:
      - name: flip
        template: flip
      - depends: flip
        name: heads
        template: heads
        when: '{{tasks.flip.outputs.result}} == heads'
      - depends: flip
        name: tails
        template: tails
        when: '{{tasks.flip.outputs.result}} == tails'
    name: d
  - name: flip
    script:
      command:
      - python
      image: python:3.7
      source: 'import os

        import sys

        sys.path.append(os.getcwd())

        import random


        result = "heads" if random.randint(0, 1) == 0 else "tails"

        print(result)

        '
  - name: heads
    script:
      command:
      - python
      image: python:3.7
      source: 'import os

        import sys

        sys.path.append(os.getcwd())

        print("it was heads")

        '
  - name: tails
    script:
      command:
      - python
      image: python:3.7
      source: 'import os

        import sys

        sys.path.append(os.getcwd())

        print("it was tails")

        '
```
