# Gitops

This example showcases the hello world example of Hera in a GitOps style. The workflow gets a global parameter set
called `msg`. This parameter has neither a `value` nor a `value_from` set. This supports the generation of a workflow
YAML file that has the full definition and supports submission via `argo submit hello.yaml -p msg="hello"`. This
parameterizes the workflow global parameter called `msg` to have a `value` of `hello`. This `hello` is then passed to
the `Task` via the global parameter `w.get_parameter('msg')`, which sets the `'{{workflow.parameters.msg}}'` on the
task parameter definition.

```python
from hera import Parameter, Task, Workflow


def say(msg: str):
    print(msg)


with Workflow(generate_name="hera-gitops-say-", inputs=[Parameter(name="msg")]) as w:
    Task("t", say, inputs=[w.get_parameter("msg")])

with open("hello.yaml", "w") as f:
    f.write(w.to_yaml())

# the above is followed up by issuing `argo submit hello.yaml -p msg="hello"`
```
