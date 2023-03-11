# Dag Diamond

> Note: This example is a replication of an Argo Workflow example in Hera. The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/dag-diamond.yaml).



## Hera

```python
from hera.workflows.container import Container
from hera.workflows.dag import DAG
from hera.workflows.models import Arguments, Parameter
from hera.workflows.task import Task
from hera.workflows.workflow import Workflow

# Showing the flexibility of hera v5
# here we defined the echo container ealier
# but add it to the workflow towards the end
# to ensure we can exactly match the upstream argo
# example and have the ability to control the output
# workflow, down to the level of being able to control the
# output list of templates
echo = Container(
    name="echo",
    image="alpine:3.7",
    command=["echo", "{{inputs.parameters.message}}"],
    inputs=[Parameter(name="message")],
)
with Workflow(
    generate_name="dag-diamond-",
    entrypoint="diamond",
) as w:
    with DAG(name="diamond"):
        A = Task(name="A", template=echo, arguments=Arguments(parameters=[Parameter(name="message", value="A")]))
        B = Task(name="B", template=echo, arguments=Arguments(parameters=[Parameter(name="message", value="B")]))
        C = Task(name="C", template=echo, arguments=Arguments(parameters=[Parameter(name="message", value="C")]))
        D = Task(name="D", template=echo, arguments=Arguments(parameters=[Parameter(name="message", value="D")]))
        A >> [B, C] >> D

    w.templates.append(echo)
```

## YAML

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: dag-diamond-
spec:
  entrypoint: diamond
  templates:
  - dag:
      tasks:
      - arguments:
          parameters:
          - name: message
            value: A
        name: A
        template: echo
      - arguments:
          parameters:
          - name: message
            value: B
        depends: A
        name: B
        template: echo
      - arguments:
          parameters:
          - name: message
            value: C
        depends: A
        name: C
        template: echo
      - arguments:
          parameters:
          - name: message
            value: D
        depends: B && C
        name: D
        template: echo
    name: diamond
  - container:
      command:
      - echo
      - '{{inputs.parameters.message}}'
      image: alpine:3.7
    inputs:
      parameters:
      - name: message
    name: echo
```
