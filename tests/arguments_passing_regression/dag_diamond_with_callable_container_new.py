from hera.workflows import (
    DAG,
    Container,
    Parameter,
    Workflow,
)

with Workflow(
    generate_name="dag-diamond-",
    entrypoint="diamond",
) as w:
    echo = Container(
        name="echo",
        image="alpine:3.7",
        command=["echo", "{{inputs.parameters.message}}"],
        inputs=[Parameter(name="message")],
        use_func_params_in_call=True,
    )
    with DAG(name="diamond"):
        A = echo("A").with_(name="A")
        B = echo("B").with_(name="B")
        C = echo("C").with_(name="C")
        D = echo("D").with_(name="D")
        A >> [B, C] >> D
