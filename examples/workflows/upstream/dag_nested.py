from hera.workflows import DAG, Container, Parameter, Workflow

echo = Container(
    name="echo",
    inputs=Parameter(name="message"),
    image="alpine:3.7",
    command=["echo", "{{inputs.parameters.message}}"],
)

with Workflow(generate_name="dag-nested-", entrypoint="diamond") as w:
    with DAG(name="nested-diamond", inputs=[Parameter(name="message")]) as nested_diamond:
        A = echo(name="A", arguments={"message": "{{inputs.parameters.message}}A"})
        B = echo(name="B", arguments={"message": "{{inputs.parameters.message}}B"})
        C = echo(name="C", arguments={"message": "{{inputs.parameters.message}}C"})
        D = echo(name="D", arguments={"message": "{{inputs.parameters.message}}D"})
        A >> [B, C] >> D

    with DAG(name="diamond") as diamond:
        A = nested_diamond(name="A", arguments={"message": "A"})
        B = nested_diamond(name="B", arguments={"message": "B"})
        C = nested_diamond(name="C", arguments={"message": "C"})
        D = nested_diamond(name="D", arguments={"message": "D"})
        A >> [B, C] >> D
