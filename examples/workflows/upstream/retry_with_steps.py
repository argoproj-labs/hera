from hera.workflows import Container, Step, Steps, Workflow
from hera.workflows.models import IntOrString, RetryStrategy

with Workflow(
    api_version="argoproj.io/v1alpha1",
    kind="Workflow",
    generate_name="retry-with-steps-",
    entrypoint="retry-with-steps",
) as w:
    with Steps(
        name="retry-with-steps",
    ) as invocator:
        Step(
            name="hello1",
            template="random-fail",
        )
        with invocator.parallel():
            Step(
                name="hello2a",
                template="random-fail",
            )
            Step(
                name="hello2b",
                template="random-fail",
            )
    Container(
        name="random-fail",
        retry_strategy=RetryStrategy(
            limit=IntOrString(
                root="10",
            ),
        ),
        args=[
            "import random; import sys; print('retries: {{retries}}'); exit_code = random.choice([0, 1, 1]); sys.exit(exit_code)"
        ],
        command=["python", "-c"],
        image="python:alpine3.6",
    )
