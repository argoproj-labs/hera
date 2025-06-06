"""This examples shows how to dynamically fan out over a list of values.

The fan-out task will consume the output of the previous task and process the list of values in parallel. We are
printing to stdout to use the `result` output parameter, but generally you should use a named output parameter.

Dynamic fan-outs are useful for batch jobs and instances where clients do not know ahead of time how many tasks/entities
they may need to process.
"""

from hera.workflows import DAG, Workflow, script


@script()
def generate():
    import json
    import random
    import sys

    # this can be anything! e.g fetch from some API, then in parallel process
    # all entities; chunk database records and process them in parallel, etc.
    json.dump([i for i in range(random.randint(8, 12))], sys.stdout)


@script()
def consume(value: int):
    print("Received value: {value}!".format(value=value))


with Workflow(generate_name="dynamic-fanout-", entrypoint="d") as w:
    with DAG(name="d"):
        g = generate()
        c = consume(with_param=g.result)
        g >> c
