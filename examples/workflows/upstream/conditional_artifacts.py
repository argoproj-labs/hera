from hera.workflows import Artifact, Script, Step, Steps, Workflow


def _flip_coin():
    import random

    print("heads" if random.randint(0, 1) == 0 else "tails")


def _heads():
    with open("result.txt", "w") as f:
        f.write("it was heads")


def _tails():
    with open("result.txt", "w") as f:
        f.write("it was tails")


with Workflow(
    generate_name="conditional-artifacts-",
    labels={
        "workflows.argoproj.io/test": "true",
    },
    annotations={
        "workflows.argoproj.io/description": "Conditional aartifacts provide a way to choose the output "
        "artifacts based on expression. "
        "In this example the main template has two steps which will run "
        "conditionall using `when` . Based on the `when` condition one of step"
        ' will not execute. The main template\'s output artifact named "result" '
        "will be set to the executed step's output."
    },
    entrypoint="main",
) as w:
    flip_coin = Script(
        name="flip-coin",
        image="python:alpine3.6",
        command=["python"],
        source=_flip_coin,
        add_cwd_to_sys_path=False,
    )
    heads = Script(
        name="heads",
        image="python:alpine3.6",
        command=["python"],
        source=_heads,
        outputs=[Artifact(name="result", path="/result.txt")],
        add_cwd_to_sys_path=False,
    )
    tails = Script(
        name="tails",
        image="python:alpine3.6",
        command=["python"],
        source=_tails,
        outputs=[Artifact(name="result", path="/result.txt")],
        add_cwd_to_sys_path=False,
    )

    with Steps(
        name="main",
        outputs=[
            Artifact(
                name="result",
                from_expression="steps['flip-coin'].outputs.result == 'heads' ? "
                "steps.heads.outputs.artifacts.result : steps.tails.outputs.artifacts.result",
            ),
        ],
    ) as s:
        Step(name="flip-coin", template=flip_coin)
        with s.parallel():
            Step(name="heads", template=heads, when="{{steps.flip-coin.outputs.result}} == heads")
            Step(name="tails", template=tails, when="{{steps.flip-coin.outputs.result}} == tails")
