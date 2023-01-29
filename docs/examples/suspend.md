# Suspend

This example showcases how to use a `suspend` template with Hera

```python
from hera import SuspendTemplate, Task, Workflow, Container

# assumes you have set a global token and host
with Workflow(generate_name="suspend-template-") as w:
    (
        Task("build", container=Container(image="docker/whalesay", command=["cowsay"], args=["hello world"]))
        >> Task("approve", suspend=SuspendTemplate())
        >> Task("delay", suspend=SuspendTemplate(duration="20"))
        >> Task("release", container=Container(image="docker/whalesay", command=["cowsay"], args=["hello world"]))
    )

w.create()
```
