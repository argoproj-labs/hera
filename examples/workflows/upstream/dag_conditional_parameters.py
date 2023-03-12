from hera.expr import g
from hera.workflows import DAG, Parameter, Script, Task, Workflow


def heads():
    print("heads")


def tails():
    print("tails")


def flip_coin():
    import random

    print("heads" if random.randint(0, 1) == 0 else "tails")


def get_script(callable):
    return Script(
        name=callable.__name__.replace("_", "-"),
        source=callable,
        add_cwd_to_sys_path=False,
        image="python:alpine3.6",
    )


with Workflow(
    generate_name="dag-conditional-parameter-",
    entrypoint="main",
) as w:
    heads_template = get_script(heads)
    tails_template = get_script(tails)
    flip_coin_template = get_script(flip_coin)

    with DAG(name="main") as main_dag:
        flip_coin_task = Task(name="flip-coin", template=flip_coin_template)
        heads_task = Task(name="heads", template=heads_template)
        tails_task = Task(name="tails", template=tails_template)
        heads_task.on_other_result(flip_coin_task, "heads")
        tails_task.on_other_result(flip_coin_task, "tails")

        expression = g.tasks["flip-coin"].outputs.result == "heads"
        expression = expression.check(g.tasks.heads.outputs.result, g.tasks.tails.outputs.result)  # type: ignore
        main_dag.outputs = [Parameter(name="stepresult", value_from={"expression": str(expression)})]
