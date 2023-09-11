from hera.workflows import DAG, Container, Parameter, Workflow

echo = Container(
    name="echo",
    inputs=Parameter(name="message"),
    image="alpine:3.7",
    command=["echo", "{{inputs.parameters.message}}"],
    use_func_params_in_call=True,
)

with Workflow(generate_name="dag-nested-", entrypoint="diamond") as w:
    with DAG(
        name="nested-diamond", inputs=[Parameter(name="message")], use_func_params_in_call=True
    ) as nested_diamond:
        A = echo("{{inputs.parameters.message}}A").with_(name="A")
        B = echo("{{inputs.parameters.message}}B").with_(name="B")
        C = echo("{{inputs.parameters.message}}C").with_(name="C")
        D = echo("{{inputs.parameters.message}}D").with_(name="D")
        A >> [B, C] >> D

    with DAG(name="diamond") as diamond:
        A = nested_diamond("A").with_(name="A")
        B = nested_diamond("B").with_(name="B")
        C = nested_diamond("C").with_(name="C")
        D = nested_diamond("D").with_(name="D")
        A >> [B, C] >> D
