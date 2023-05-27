from hera.workflows import DAG, Container, Parameter, Workflow

one_job = Container(
    name="one-job",
    inputs=Parameter(name="msg"),
    image="alpine",
    command=["/bin/sh", "-c"],
    args=["echo {{inputs.parameters.msg}}; sleep 10"],
)

with Workflow(generate_name="parallelism-nested-dag-", entrypoint="A") as w:
    with DAG(name="B", inputs=Parameter(name="msg")) as B:
        c1 = one_job(name="c1", msg="{{inputs.parameters.msg}} c1")
        c2 = one_job(name="c2", msg="{{inputs.parameters.msg}} c2")
        c3 = one_job(name="c3", msg="{{inputs.parameters.msg}} c3")
        c1 >> [c2, c3]

    with DAG(name="A", parallelism=2) as A:
        b1 = B(name="b1", msg="1")
        b2 = B(name="b2", msg="2")
        b3 = B(name="b3", msg="3")
        b4 = B(name="b4", msg="4")
        b5 = B(name="b5", msg="5")
        b1 >> [b2, b3, b4] >> b5
