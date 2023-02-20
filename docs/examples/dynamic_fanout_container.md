# Dynamic Fanout Container

This example showcases how clients can use Hera to dynamically generate tasks that process outputs from one task in
parallel. Differ from dynamic_fanout.py, this example uses a container to generate the tasks and the dynamically
created tasks are also container only.
More details can be found here: https://github.com/argoproj-labs/hera-workflows/issues/250

```python
from hera.workflows import Parameter, Task, Workflow

# assumes you used `hera.set_global_token` and `hera.set_global_host` so that the workflow can be submitted
with Workflow("dynamic-fanout-container") as w:
    # this can be anything! e.g. fetch from some API, then in parallel process all entities; chunk database records
    # and process them in parallel, etc.
    generate_task = Task(
        "generate",
        image="alpine:latest",
        command=["echo", '[{"value": "a"}, {"value": "b"}, {"value": "c"}]'],
    )
    fanout_task = Task(
        "fanout",
        with_param=generate_task.get_result(),  # this make the task fan out over the `with_param`
        # `inputs` sets the correct input parameter so the result is used
        inputs=[Parameter(name="value", value="{{item.value}}")],
        image="alpine:latest",
        command=["echo", "{{inputs.parameters.value}}"],
    )
    generate_task >> fanout_task

w.create()
```
