# Output Results Workflow





## Hera

```python
from hera.expr import g
from hera.workflows.container_set import ContainerNode, ContainerSet
from hera.workflows.dag import DAG
from hera.workflows.models import Arguments
from hera.workflows.parameter import Parameter
from hera.workflows.script import Script
from hera.workflows.task import Task
from hera.workflows.workflow import Workflow


def _check():
    assert "{{inputs.parameters.x}}" == "hi"


with Workflow(
    generate_name="graph-",
    entrypoint="main",
    labels={"workflows.argoproj.io/test": "true"},
    annotations={
        "workflows.argoproj.io/description": "This workflow demonstrates collecting outputs (specifically the stdout result) "
        'from a pod. Specifically, you must have a container named "main".',
        "workflows.argoproj.io/version": ">= 3.1.0",
    },
) as w:
    with ContainerSet(name="group") as group:
        ContainerNode(name="main", image="python:alpine:3.6", command=["python", "-c"], args=["print('hi')"])

    verify = Script(
        source=_check,
        image="python:alpine3.6",
        command=["python"],
        inputs=[Parameter(name="x")],
        add_cwd_to_sys_path=False,
    )
    with DAG(name="main") as dag:
        a = Task(name="a", template=group)
        b = Task(
            name="b",
            arguments=Arguments(parameters=[Parameter(name="x", value=f"{g.tasks.a.outputs.result:$}")]),
            template=verify,
        )
```

## YAML

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  annotations:
    workflows.argoproj.io/description: This workflow demonstrates collecting outputs
      (specifically the stdout result) from a pod. Specifically, you must have a container
      named "main".
    workflows.argoproj.io/version: '>= 3.1.0'
  generateName: graph-
  labels:
    workflows.argoproj.io/test: 'true'
spec:
  entrypoint: main
  templates:
  - containerSet:
      containers:
      - args:
        - print('hi')
        command:
        - python
        - -c
        image: python:alpine:3.6
        name: main
    name: group
  - inputs:
      parameters:
      - name: x
    script:
      command:
      - python
      image: python:alpine3.6
      source: 'assert "{{inputs.parameters.x}}" == "hi"

        '
  - dag:
      tasks:
      - name: a
        template: group
      - arguments:
          parameters:
          - name: x
            value: '{{tasks.a.outputs.result}}'
        name: b
    name: main
```
