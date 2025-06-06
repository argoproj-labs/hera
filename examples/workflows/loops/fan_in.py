"""This example shows how to collect values in a "fan-in" task after the fan-out.

This also works for the `result` output parameter (as long as nothing else is in stdout!).
"""

from hera.workflows import DAG, Parameter, Workflow, script
from hera.workflows.models import ValueFrom


@script()
def generate():
    import json
    import sys

    json.dump([{"value": i} for i in range(10)], sys.stdout)


@script(
    outputs=[
        Parameter(
            name="value",
            value_from=ValueFrom(path="/tmp/value"),
        )
    ]
)
def fanout(my_dict: dict):
    print("Received object: {my_dict}!".format(my_dict=my_dict))
    # Output the content of the "value" key in the dict
    value = my_dict["value"]
    with open("/tmp/value", "w") as f:
        f.write(str(value))


@script()
def fanin(values: list):
    print("Received values: {values}!".format(values=values))


with Workflow(generate_name="fan-in-", entrypoint="d") as w:
    with DAG(name="d"):
        g = generate()
        fout = fanout(with_param=g.result)
        fin = fanin(arguments={"values": fout.get_parameter("value")})
        g >> fout >> fin
