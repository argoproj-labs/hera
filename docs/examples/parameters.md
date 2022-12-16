# Parameters

This example showcases how one can set parameters on Hera tasks

```python
from hera import Task, Workflow


def hello(a: str, b: int, c: dict):
    print(f"a = {a}, type(a) = {type(a)}")
    print(f"b = {b}, type(b) = {type(b)}")
    print(f"c = {c}, type(c) = {type(c)}")


# assumes you used `hera.set_global_token` and `hera.set_global_host` so that the workflow can be submitted
with Workflow("parameters") as w:
    Task('hello', source=hello, inputs={"a": "world", "b": 42, "c": {"k": "v"}})

w.create()
```
