"""
This example showcases how clients can use Hera to dynamically generate tasks that process outputs from one task in
parallel. This is useful for batch jobs and instances where clients do not know ahead of time how many tasks/entities
they may need to process. The fanout occurs over independent JSON payloads coming from the generate script
"""
from hera.workflows import DAG, Workflow, script


@script()
def generate():
    import json
    import sys

    # this can be anything! e.g fetch from some API, then in parallel process all entities; chunk database records
    # and process them in parallel, etc.
    json.dump([{"p1": i + 1, "p2": i + 2, "p3": i + 3} for i in range(10)], sys.stdout)


@script()
def consume(p1: str, p2: str, p3: str):
    print("Received p1={p1}, p2={p2}, p3={p3}".format(p1=p1, p2=p2, p3=p3))


# assumes you used `hera.set_global_token` and `hera.set_global_host` so that the workflow can be submitted
with Workflow(generate_name="dynamic-fanout-", entrypoint="d") as w:
    with DAG(name="d"):
        g = generate()
        c = consume(with_param=g.result)
        g >> c
