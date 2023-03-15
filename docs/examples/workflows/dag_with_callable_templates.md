# Dag With Callable Templates





## Hera

```python
from hera.workflows import (
    DAG,
    Container,
    Parameter,
    Workflow,
)

with Workflow(
    generate_name="callable-templates-",
    entrypoint="hello-world",
) as w:
    echo = Container(
        name="echo",
        image="alpine:3.7",
        command=["echo", "{{inputs.parameters.message}}"],
        inputs=[Parameter(name="message")],
    )

    with DAG(name="hello-world") as d:
        (
            echo(name="hello1", arguments=[Parameter(name="message", value="hello1")])
            >> echo(name="hello2", arguments=[Parameter(name="message", value="hello2")])
        )
```

## YAML

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: callable-templates-
spec:
  entrypoint: hello-world
  templates:
  - container:
      command:
      - echo
      - '{{inputs.parameters.message}}'
      image: alpine:3.7
    inputs:
      parameters:
      - name: message
    name: echo
  - dag:
      tasks:
      - arguments:
          parameters:
          - name: message
            value: hello1
        name: hello1
        template: echo
      - arguments:
          parameters:
          - name: message
            value: hello2
        depends: hello1
        name: hello2
        template: echo
    name: hello-world
```
