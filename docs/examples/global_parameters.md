# Global parameters

```python
from hera import Parameter, Task, Workflow


def foo(v):
    print(v)


with Workflow("global-parameters", parameters=[Parameter("v", "42")]) as w:
    Task("t", foo, inputs=[w.get_parameter("v")])

w.create()

```