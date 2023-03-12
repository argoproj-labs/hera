from hera.workflows import (
    DAG,
    Container,
    Parameter,
    Task,
    Workflow,
    models as m,
)

# Showing the flexibility of hera v5
# here we defined the echo container ealier
# but add it to the workflow towards the end
# to ensure we can exactly match the upstream argo
# example and have the ability to control the output
# workflow, down to the level of being able to control the
# output list of templates
echo = Container(
    name="echo",
    image="alpine:3.7",
    command=["echo", "{{inputs.parameters.message}}"],
    inputs=[Parameter(name="message")],
)
with Workflow(
    generate_name="dag-diamond-",
    entrypoint="diamond",
) as w:
    with DAG(name="diamond"):
        A = Task(name="A", template=echo, arguments=m.Arguments(parameters=[Parameter(name="message", value="A")]))
        B = Task(name="B", template=echo, arguments=m.Arguments(parameters=[Parameter(name="message", value="B")]))
        C = Task(name="C", template=echo, arguments=m.Arguments(parameters=[Parameter(name="message", value="C")]))
        D = Task(name="D", template=echo, arguments=m.Arguments(parameters=[Parameter(name="message", value="D")]))
        A >> [B, C] >> D

    w.templates.append(echo)
