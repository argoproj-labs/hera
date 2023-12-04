from hera.workflows import DAG, Parameter, Workflow, script
from hera.workflows.models import ValueFrom


@script()
def generate():
    import json
    import sys

    json.dump([{"value": i} for i in range(10)], sys.stdout)


@script(outputs=[Parameter(name="value", value_from=ValueFrom(path="/tmp/value"))])
def fanout(object: dict):
    print("Received object: {object}!".format(object=object))
    # Output the content of the "value" key in the object
    value = object["value"]
    with open("/tmp/value", "w") as f:
        f.write(str(value))


@script()
def fanin(values: list):
    print("Received values: {values}!".format(values=values))


# assumes you used `hera.set_global_token` and `hera.set_global_host` so that the workflow can be submitted
with Workflow(generate_name="dynamic-fanout-fanin", entrypoint="d") as w:
    with DAG(name="d"):
        g = generate()
        fout = fanout(with_param=g.result)
        fin = fanin(arguments=fout.get_parameter("value").with_name("values"))
        g >> fout >> fin
