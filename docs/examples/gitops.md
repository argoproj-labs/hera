# Sample GitOps pattern

This example showcases the hello world example of Hera in a GitOps style. The workflow gets a global parameter set
called `msg`. This parameter has neither a `value` nor a `value_from` set. This supports the generation of a workflow
YAML file that has the full definition and supports submission via `argo submit hello.yaml -p msg="hello"`. This
parameterizes the workflow global parameter called `msg` to have a `value` of `hello`. This `hello` is then passed to
the `Task` via the global parameter `w.get_parameter('msg')`, which sets the `'{{workflow.parameters.msg}}'` on the
task parameter definition.

## Workflow definition (Python)

```python
from hera import Task, Workflow, Parameter


def say(msg: str):
    print(msg)


with Workflow("hera-gitops-say", parameters=[Parameter('msg')]) as w:
    Task("t", say, inputs=[w.get_parameter('msg')])

with open('hello.yaml', 'w') as f:
    f.write(w.to_yaml())
```

## GitOps style/local submission

```shell
argo submit hello.yaml -p msg="hello"
```
