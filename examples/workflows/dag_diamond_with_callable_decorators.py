from hera.workflows import (
    DAG,
    Workflow,
    script,
)

@script(add_cwd_to_sys_path=False, image="python:alpine3.6")
def echo(message):
    print(message)


with Workflow(generate_name="dag-diamond-", entrypoint="diamond") as w:
    with DAG(name="diamond"):
        A = echo(name="A", message="A")
        B = echo(name="B", message="B")
        C = echo(name="C", message="C")
        D = echo(name="D", message="D")
        A >> [B, C] >> D

