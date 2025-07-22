from hera.workflows import DAG, Container, Step, Steps, Task, Workflow

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    generate_name="resubmit-",
    entrypoint="rand-fail-dag",
) as w:
    with DAG(
        name="rand-fail-dag",
    ) as invocator:
        Task(
            name="A",
            template="random-fail",
        )
        Task(
            name="B",
            template="rand-fail-steps",
        )
        Task(
            name="C",
            template="random-fail",
            depends="B",
        )
        Task(
            name="D",
            template="random-fail",
            depends="A && B",
        )
    with Steps(
        name="rand-fail-steps",
    ) as invocator:
        with invocator.parallel():
            Step(
                name="randfail1a",
                template="random-fail",
            )
            Step(
                name="randfail1b",
                template="random-fail",
            )
        with invocator.parallel():
            Step(
                name="randfail2a",
                template="random-fail",
            )
            Step(
                name="randfail2b",
                template="random-fail",
            )
            Step(
                name="randfail2c",
                template="random-fail",
            )
            Step(
                name="randfail2d",
                template="random-fail",
            )
    Container(
        name="random-fail",
        args=[
            "import random; import sys; exit_code = random.choice([0, 0, 1]); print('exiting with code {}'.format(exit_code)); sys.exit(exit_code)"
        ],
        command=["python", "-c"],
        image="python:alpine3.6",
    )
