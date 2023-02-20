# Multiple Dependencies

This simple example showcases how to set a single task as a dependency of multiple other tasks

```python
from hera.workflows import Task, Workflow


def foo():
    print(42)


def hello():
    print("Hello, world!")


with Workflow("multiple-dependencies") as w:
    Task("hello-world", hello) >> [Task("foo1", foo), Task("foo2", foo), Task("foo3", foo)]
w.create()
```
