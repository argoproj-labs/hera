"""
This example showcases how clients can use Hera to dynamically generate tasks that process outputs from one task in
parallel. This is useful for batch jobs and instances where clients do not know ahead of time how many tasks/entities
they may need to process.
"""
from hera import Task, Workflow, WorkflowService


def generate():
    import json
    import sys

    # this can be anything! e.g fetch from some API, then in parallel process all entities; chunk database records
    # and process them in parallel, etc.
    json.dump([i for i in range(10)], sys.stdout)


def consume(value: int):
    print(f"Received value: {value}!")


ws = WorkflowService(host="https://my-argo-server.com", token="my-auth-token")

with Workflow("dynamic-fanout", service=ws) as w:
    generate_task = Task("generate", generate)
    consume_task = Task("consume", consume, with_param=generate_task.get_result())

    generate_task >> consume_task

w.create()
