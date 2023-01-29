# Workflow Template Global Parameters



```python
from hera import Parameter, Task, WorkflowTemplate


def foo(v):
    print(v)


# assumes you used `hera.set_global_token` and `hera.set_global_host` so that the workflow can be submitted
with WorkflowTemplate(generate_name="global-parameters-", inputs=[Parameter(name="v", value=42)]) as w:
    Task("t", foo, inputs=[w.get_parameter("v")])

w.create()
```
