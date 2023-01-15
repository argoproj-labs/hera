from hera import Parameter, Task, ValueFrom, Workflow


def generate():
    import json
    import sys

    # this can be anything! e.g fetch from some API, then in parallel process all entities; chunk database records
    # and process them in parallel, etc.
    json.dump([{"value": i} for i in range(10)], sys.stdout)


def fanout(object: dict):
    print(f"Received object: {object}!")
    # Output the content of the "value" key in the object
    value = object["value"]
    with open("/tmp/value", "w") as f:
        f.write(str(value))


def fanin(values: list):
    print(f"Received values: {values}!")


# assumes you used `hera.set_global_token` and `hera.set_global_host` so that the workflow can be submitted
with Workflow("dynamic-fanout-fanin") as w:
    generate_task = Task("generate", generate)
    fanout_task = Task(
        "fanout",
        fanout,
        with_param=generate_task.get_result(),
        outputs=[Parameter(name="value", value_from=ValueFrom(path="/tmp/value"))],
    )
    fanin_task = Task("fanin", fanin, inputs=[fanout_task.get_parameters_as("values")])

    generate_task >> fanout_task >> fanin_task

w.create()
