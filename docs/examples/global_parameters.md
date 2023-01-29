# Global Parameters



```python
from hera import Parameter, Task, Workflow


def foo(v):
    print(v)


with Workflow(generate_name="global-parameters-", inputs=[Parameter(name="v", value=42)]) as w:
    Task("t", foo, inputs=[w.get_parameter("v")])

w.create()
```
