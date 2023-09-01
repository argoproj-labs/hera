from hera.workflows import (
    DAG,
    Workflow,
    script,
)


@script(add_cwd_to_sys_path=False, image="python:alpine3.6", directly_callable=True)
def echo(message):
    print(message)


with Workflow(generate_name="dag-diamond-", entrypoint="diamond") as w:
    with DAG(name="diamond"):
        A = echo("A").with_(name="A")
        B = echo("B").with_(name="B")
        C = echo("C").with_(name="C")
        D = echo("D").with_(name="D")
        A >> [B, C] >> D
