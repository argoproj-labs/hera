# Conditional

This example showcases conditional execution on success, failure, and error

```python
from hera import Task, Workflow


def random():
    import random

    p = random.random()
    if p <= 0.5:
        raise Exception("failure")
    print("success")


def success():
    print("success")


def failure():
    print("failure")


with Workflow("conditional") as w:
    r = Task("random", random)
    s = Task("success", success)
    f = Task("failure", failure)

    r.on_success(s)
    r.on_failure(f)

w.create()
```
