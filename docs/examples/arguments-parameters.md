# Arguments-Parameters

This example showcases how to set up arguments and parameters.

https://github.com/argoproj/argo-workflows/blob/master/examples/arguments-parameters.yaml

```python
from hera import Container, Parameter, Task, Workflow

with Workflow(generate_name="arguments-parameters-", inputs=[Parameter(name="message", value="hello world")]) as w:
    Task(
        "whalesay",
        inputs=[Parameter(name="message")],
        container=Container(image="docker/whalesay:latest", command=["cowsay"]),
        args=["{{inputs.parameters.message}}"],
    )

w.create()
```
