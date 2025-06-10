"""This examples shows how to dynamically fan out over a list of values using `Container` templates.

The command `len=$((8 + RANDOM % 4)); json=$(seq 1 "$len" | paste -sd, -); echo "[$json]"` produces a list of random
length (between 8 and 12), which is then echoed in json format. This matches the [dynamic fanout](dynamic_fanout.md)
example that uses Python. In this example, we must specify the arguments as `Container` does not automatically match
them for us.
"""

from hera.workflows import DAG, Container, Parameter, Workflow

generate = Container(
    name="generate",
    image="alpine:latest",
    command=['len=$((8 + RANDOM % 4)); json=$(seq 1 "$len" | paste -sd, -); echo "[$json]"'],
)

fanout = Container(
    name="fanout",
    inputs=[Parameter(name="value")],
    image="alpine:latest",
    command=["echo", "{{inputs.parameters.value}}"],
)

with Workflow(
    generate_name="dynamic-fanout-container-",
    entrypoint="d",
) as w:
    with DAG(name="d"):
        g = generate()
        f = fanout(arguments={"value": "{{item}}"}, with_param=g.result)
        g >> f
