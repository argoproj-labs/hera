# Hello Hera

This example showcases the hello world example of Hera

```python
from hera import Task, Workflow


def hello():
    print("Hello, Hera!")


# assumes you used `hera.set_global_token` and `hera.set_global_host` so that the workflow can be submitted
with Workflow(generate_name="hello-hera-") as w:
    Task("t", hello)

w.create()
```
