"""
This example showcases how clients can use Hera to dynamically generate tasks that process outputs from one task in
parallel. This is useful for batch jobs and instances where clients do not know ahead of time how many tasks/entities
they may need to process.
"""
from hera.workflows import DAG, Workflow, script


@script()
def generate():
    import json
    import sys

    # this can be anything! e.g fetch from some API, then in parallel process all entities; chunk database records
    # and process them in parallel, etc.
    json.dump([i for i in range(10)], sys.stdout)


@script(use_func_params_in_call=True)
def consume(value: int):
    print("Received value: {value}!".format(value=value))


# assumes you used `hera.set_global_token` and `hera.set_global_host` so that the workflow can be submitted
with Workflow(generate_name="dynamic-fanout-", entrypoint="d") as w:
    with DAG(name="d"):
        g = generate()
        c = consume().with_(with_param=g.result)
        g >> c
