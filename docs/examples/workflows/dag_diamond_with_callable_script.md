# Dag Diamond With Callable Script





## Hera

```python
from hera.workflows import (
    DAG,
    Parameter,
    Script,
    Workflow,
)


def my_print_script(message):
    print(message)


def get_script(callable):
    # note that we have the _option_ to set `inputs=Parameter(name="message")`, but Hera infers the `Parameter`s
    # that are necessary based on the passed in callable!
    return Script(
        name=callable.__name__.replace("_", "-"),
        source=callable,
        add_cwd_to_sys_path=False,
        image="python:alpine3.6",
    )


with Workflow(
    generate_name="dag-diamond-",
    entrypoint="diamond",
) as w:
    echo = get_script(my_print_script)

    with DAG(name="diamond"):
        A = echo(name="A", arguments=[Parameter(name="message", value="A")])
        B = echo(name="B", arguments=[Parameter(name="message", value="B")])
        C = echo(name="C", arguments=[Parameter(name="message", value="C")])
        D = echo(name="D", arguments=[Parameter(name="message", value="D")])
        A >> [B, C] >> D
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
  - inputs:
      parameters:
      - name: message
    name: my-print-script
    script:
      command:
      - python
      image: python:alpine3.6
      source: 'import json

        try: message = json.loads(r''''''{{inputs.parameters.message}}'''''')

        except: message = r''''''{{inputs.parameters.message}}''''''


        print(message)

        '
  - dag:
      tasks:
      - arguments:
          parameters:
          - name: message
            value: A
        name: A
        template: my-print-script
      - arguments:
          parameters:
          - name: message
            value: B
        depends: A
        name: B
        template: my-print-script
      - arguments:
          parameters:
          - name: message
            value: C
        depends: A
        name: C
        template: my-print-script
      - arguments:
          parameters:
          - name: message
            value: D
        depends: B && C
        name: D
        template: my-print-script
    name: diamond
```
