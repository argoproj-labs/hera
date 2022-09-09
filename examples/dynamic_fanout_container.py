"""
This example showcases how clients can use Hera to dynamically generate tasks that process outputs from one task in
parallel. Differ from dynamic_fanout.py, this example uses a container to generate the tasks and the dynamically created
tasks are also container only.
More details can be found here: https://github.com/argoproj-labs/hera-workflows/issues/250
"""

from hera import InputFrom, Task, Workflow, WorkflowService


with Workflow(
    "dynamic-fanout-container", service=WorkflowService(host="https://my-argo-server.com", token="my-auth-token"),
) as w:

    # this can be anything! e.g fetch from some API, then in parallel process all entities; chunk database records
    # and process them in parallel, etc.
    generate_task = Task(
        "generate", image="alpine:latest", command=["echo", '[{"value": "a"}, {"value": "b"}, {"value": "c"}]'],
    )

    fanout_task = Task(
        "fanout",
        input_from=InputFrom("generate", ["value"]),
        image="alpine:latest",
        command=["echo"],
        args=["{{inputs.parameters.value}}"],
    )

    generate_task >> fanout_task

w.create()
