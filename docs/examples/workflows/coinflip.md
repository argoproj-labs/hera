# Coinflip





## Hera

```python
from hera.workflows import Container, Script, Steps, Workflow


def flip_coin_func() -> None:
    import random

    result = "heads" if random.randint(0, 1) == 0 else "tails"
    print(result)


with Workflow(
    generate_name="coinflip-",
    annotations={
        "workflows.argoproj.io/description": (
            "This is an example of coin flip defined as a sequence of conditional steps."
        ),
    },
) as w:
    heads = Container(
        name="heads",
        image="alpine:3.6",
        command=["sh", "-c"],
        args=["echo 'it was heads'"],
    )
    tails = Container(
        name="tails",
        image="alpine:3.6",
        command=["sh", "-c"],
        args=["echo 'it was tails'"],
    )

    flip_coin = Script(
        name="flip-coin",
        image="python:alpine3.6",
        command=["python"],
        source=flip_coin_func,
    )

    with Steps(name="coinflip") as s:
        fc = flip_coin()

        with s.parallel():
            heads(when=f"{fc.result} == heads")
            tails(when=f"{fc.result} == tails")
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
  - name: flip-coin
    script:
      command:
      - python
      image: python:alpine3.6
      source: 'import os

        import sys

        sys.path.append(os.getcwd())

        import random


        result = "heads" if random.randint(0, 1) == 0 else "tails"

        print(result)

        '
  - name: coinflip
    steps:
    - - name: flip-coin
        template: flip-coin
    - - name: heads
        template: heads
        when: '{{steps.flip-coin.outputs.result}} == heads'
      - name: tails
        template: tails
        when: '{{steps.flip-coin.outputs.result}} == tails'
```
