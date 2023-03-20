# Loops Param Result

> Note: This example is a replication of an Argo Workflow example in Hera. The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/loops-param-result.yaml).



## Hera

```python
from hera.workflows import Container, Parameter, Script, Steps, Workflow


def _gen_number_list():
    import json
    import sys

    json.dump([i for i in range(20, 31)], sys.stdout)


with Workflow(
    generate_name="loops-param-result-",
    entrypoint="loop-param-result-example",
) as w:
    gen_number_list = Script(
        name="gen-number-list",
        image="python:alpine3.6",
        command=["python"],
        source=_gen_number_list,
        add_cwd_to_sys_path=False,
    )
    sleep_n_sec = Container(
        name="sleep-n-sec",
        inputs=Parameter(name="seconds"),
        image="alpine:latest",
        command=["sh", "-c"],
        args=[
            "echo sleeping for {{inputs.parameters.seconds}} seconds; sleep {{inputs.parameters.seconds}}; echo done"
        ],
    )

    with Steps(name="loop-param-result-example"):
        g = gen_number_list(name="generate")
        sleep_n_sec(
            name="sleep",
            arguments=Parameter(name="seconds", value="{{item}}"),
            with_param=g.result,
        )
```

## YAML

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: loops-param-result-
spec:
  entrypoint: loop-param-result-example
  templates:
  - name: gen-number-list
    script:
      command:
      - python
      image: python:alpine3.6
      source: 'import json

        import sys


        json.dump([i for i in range(20, 31)], sys.stdout)

        '
  - container:
      args:
      - echo sleeping for {{inputs.parameters.seconds}} seconds; sleep {{inputs.parameters.seconds}};
        echo done
      command:
      - sh
      - -c
      image: alpine:latest
    inputs:
      parameters:
      - name: seconds
    name: sleep-n-sec
  - name: loop-param-result-example
    steps:
    - - name: generate
        template: gen-number-list
    - - arguments:
          parameters:
          - name: seconds
            value: '{{item}}'
        name: sleep
        template: sleep-n-sec
        withParam: '{{steps.generate.outputs.result}}'
```
