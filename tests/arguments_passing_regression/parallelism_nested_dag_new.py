from hera.workflows import DAG, Container, Parameter, Workflow

one_job = Container(
    name="one-job",
    inputs=Parameter(name="msg"),
    image="alpine",
    command=["/bin/sh", "-c"],
    args=["echo {{inputs.parameters.msg}}; sleep 10"],
    use_func_params_in_call=True,
)

with Workflow(generate_name="parallelism-nested-dag-", entrypoint="A") as w:
    with DAG(name="B", inputs=Parameter(name="msg"), use_func_params_in_call=True) as B:
        c1 = one_job("{{inputs.parameters.msg}} c1").with_(name="c1")
        c2 = one_job("{{inputs.parameters.msg}} c2").with_(name="c2")
        c3 = one_job("{{inputs.parameters.msg}} c3").with_(name="c3")
        c1 >> [c2, c3]

    with DAG(name="A", parallelism=2) as A:
        b1 = B("1").with_(name="b1")
        b2 = B("2").with_(name="b2")
        b3 = B("3").with_(name="b3")
        b4 = B("4").with_(name="b4")
        b5 = B("5").with_(name="b5")
        b1 >> [b2, b3, b4] >> b5
