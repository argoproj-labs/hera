# Steps With Callable Templates





## Hera

```python
from hera.workflows import (
    Container,
    Parameter,
    Steps,
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

    with Steps(name="hello-world") as s:
        echo(name="hello1", arguments=[Parameter(name="message", value="hello1")])

        with s.parallel():
            echo(name="hello2a", arguments=[Parameter(name="message", value="hello2a")])
            echo(name="hello2b", arguments=[Parameter(name="message", value="hello2b")])
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
  - name: hello-world
    steps:
    - - arguments:
          parameters:
          - name: message
            value: hello1
        name: hello1
        template: echo
    - - arguments:
          parameters:
          - name: message
            value: hello2a
        name: hello2a
        template: echo
      - arguments:
          parameters:
          - name: message
            value: hello2b
        name: hello2b
        template: echo
```
