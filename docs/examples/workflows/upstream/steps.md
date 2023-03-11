# Steps

> Note: This example is a replication of an Argo Workflow example in Hera. The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/steps.yaml).



## Hera

```python
from hera.workflows.container import Container
from hera.workflows.models import Parameter
from hera.workflows.steps import Step, Steps
from hera.workflows.workflow import Workflow

whalesay = Container(
    name="whalesay",
    inputs=[Parameter(name="message")],
    image="docker/whalesay",
    command=["cowsay"],
    args=["{{inputs.parameters.message}}"],
)

with Workflow(
    generate_name="steps-",
    entrypoint="hello-hello-hello",
) as w:
    with Steps(name="hello-hello-hello") as s:
        Step(
            name="hello1",
            template="whalesay",
            arguments=[Parameter(name="message", value="hello1")],
        )

        with s.parallel():
            Step(
                name="hello2a",
                template="whalesay",
                arguments=[Parameter(name="message", value="hello2a")],
            )
            Step(
                name="hello2b",
                template="whalesay",
                arguments=[Parameter(name="message", value="hello2b")],
            )

    w.templates.append(whalesay)
```

## YAML

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: steps-
spec:
  entrypoint: hello-hello-hello
  templates:
  - name: hello-hello-hello
    steps:
    - - arguments:
          parameters:
          - name: message
            value: hello1
        name: hello1
        template: whalesay
    - - arguments:
          parameters:
          - name: message
            value: hello2a
        name: hello2a
        template: whalesay
      - arguments:
          parameters:
          - name: message
            value: hello2b
        name: hello2b
        template: whalesay
  - container:
      args:
      - '{{inputs.parameters.message}}'
      command:
      - cowsay
      image: docker/whalesay
    inputs:
      parameters:
      - name: message
    name: whalesay
```
