from typing import cast

from hera.expr import g
from hera.workflows import DAG, Parameter, Script, Task, Workflow


def heads():
    print("heads")


def tails():
    print("tails")


# fmt: off
def flip_coin():
    import random
    print("heads" if random.randint(0,1) == 0 else "tails")
# fmt: on


def get_script(callable):
    return Script(
        name=callable.__name__.replace("_", "-"),
        source=callable,
        add_cwd_to_sys_path=False,
        image="python:alpine3.6",
    )


heads_template = get_script(heads)
tails_template = get_script(tails)
flip_coin_template = get_script(flip_coin)

with Workflow(
    generate_name="dag-conditional-parameter-",
    entrypoint="main",
    labels={"workflows.argoproj.io/test": "true"},
    annotations={
        "workflows.argoproj.io/description": (
            "Conditional parameters provide a way to choose the output parameters "
            "based on expression.\n\nIn this example DAG template has two task which"
            " will run conditionally based on `when`.\n\nBased on this condition one"
            " of task may not execute."
            " The template's output parameter will be set to the\nexecuted taks's output result.\n"
        ),
        "workflows.argoproj.io/version": ">= 3.1.0",
    },
) as w:
    with DAG(name="main") as main_dag:
        flip_coin_task = Task(name="flip-coin", template=flip_coin_template)
        heads_task = Task(name="heads", template=heads_template)
        tails_task = Task(name="tails", template=tails_template)
        heads_task.on_other_result(flip_coin_task, "heads")
        tails_task.on_other_result(flip_coin_task, "tails")

    expression = g.tasks["flip-coin"].outputs.result == "heads"
    expression = expression.check(g.tasks.heads.outputs.result, g.tasks.tails.outputs.result)  # type: ignore
    cast(list, main_dag.outputs).append(Parameter(name="stepresult", value_from={"expression": str(expression)}))
    w.templates.extend((flip_coin_template, heads_template, tails_template))
