from hera.expr import g
from hera.workflows import DAG, Parameter, Workflow, script


@script(add_cwd_to_sys_path=False, image="python:alpine3.6", directly_callable=True)
def heads():
    print("heads")


@script(add_cwd_to_sys_path=False, image="python:alpine3.6", directly_callable=True)
def tails():
    print("tails")


@script(add_cwd_to_sys_path=False, image="python:alpine3.6", directly_callable=True)
def flip_coin():
    import random

    print("heads" if random.randint(0, 1) == 0 else "tails")


with Workflow(
    generate_name="dag-conditional-parameter-",
    entrypoint="main",
) as w:
    with DAG(name="main") as main_dag:
        fc = flip_coin().with_(name="flip-coin")
        h = heads().with_(name="heads").on_other_result(fc, "heads")
        t = tails().with_(name="tails").on_other_result(fc, "tails")

        expression = g.tasks["flip-coin"].outputs.result == "heads"
        expression = expression.check(g.tasks.heads.outputs.result, g.tasks.tails.outputs.result)  # type: ignore
        main_dag.outputs = [Parameter(name="stepresult", value_from={"expression": str(expression)})]
