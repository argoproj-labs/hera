"""This example shows how you can fan-out over a JSON payload (a JSON list of dicts), and let Hera match the arguments for you."""

from hera.workflows import DAG, Workflow, script


@script()
def generate():
    import json
    import sys

    # this can be anything! e.g fetch from some API, then in parallel process
    # all entities; chunk database records and process them in parallel, etc.
    json.dump([{"p1": i + 1, "p2": i + 2, "p3": i + 3} for i in range(10)], sys.stdout)


@script()
def consume(p1: str, p2: str, p3: str):
    print("Received p1={p1}, p2={p2}, p3={p3}".format(p1=p1, p2=p2, p3=p3))


with Workflow(generate_name="json-payload-fanout-", entrypoint="d") as w:
    with DAG(name="d"):
        g = generate()
        c = consume(with_param=g.result)
        g >> c
