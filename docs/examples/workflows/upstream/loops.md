# Loops

> Note: This example is a replication of an Argo Workflow example in Hera. The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/loops.yaml).

apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: loops-
spec:
  entrypoint: loop-example
  templates:
  - name: loop-example
    steps:
    - - name: print-message
        template: whalesay
        arguments:
          parameters:
          - name: message
            value: "{{item}}"
        withItems:
        - hello world
        - goodbye world

  - name: whalesay
    inputs:
      parameters:
      - name: message
    container:
      image: docker/whalesay:latest
      command: [cowsay]
      args: ["{{inputs.parameters.message}}"]

## Hera

```python
from hera.workflows import Workflow, Container, Parameter, Steps

with Workflow(generate_name="loops-", entrypoint="loop-example") as w:
    whalesay = Container(
        name="whalesay",
        inputs=Parameter(name="message"),
        image="docker/whalesay:latest",
        command=["cowsay"],
        args=["{{inputs.parameters.message}}"],
    )

    with Steps(name="loop-example"):
        whalesay(
            name="print-message",
            arguments={"message": "{{item}}"},
            with_items=["hello world", "goodbye world"],
        )
```

## YAML

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: loops-
spec:
  entrypoint: loop-example
  templates:
  - container:
      args:
      - '{{inputs.parameters.message}}'
      command:
      - cowsay
      image: docker/whalesay:latest
    inputs:
      parameters:
      - name: message
    name: whalesay
  - name: loop-example
    steps:
    - - arguments:
          parameters:
          - name: message
            value: '{{item}}'
        name: print-message
        template: whalesay
        withItems:
        - hello world
        - goodbye world
```
