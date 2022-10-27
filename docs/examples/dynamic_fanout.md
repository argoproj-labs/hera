# Dynamic fanout

This example showcases how clients can use Hera to dynamically generate tasks that process outputs from one task in
parallel. This is useful for batch jobs and instances where clients do not know ahead of time how many tasks/entities
they may need to process.

```python
from hera import Task, Workflow


def generate():
    import json
    import sys

    # this can be anything! e.g fetch from some API, then in parallel process all entities; chunk database records
    # and process them in parallel, etc.
    json.dump([i for i in range(10)], sys.stdout)


def consume(value: int):
    print(f"Received value: {value}!")


# assumes you used `hera.set_global_token` and `hera.set_global_host` so that the workflow can be submitted
with Workflow("dynamic-fanout") as w:
    generate_task = Task("generate", generate)
    consume_task = Task("consume", consume, with_param=generate_task.get_result())

    generate_task >> consume_task

w.create()
```
