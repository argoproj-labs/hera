from hera.workflows import Container, RetryStrategy, Workflow

with Workflow(generate_name="retry-container-", entrypoint="retry-container") as w:
    Container(
        name="retry-container",
        image="python:alpine3.6",
        command=["python", "-c"],
        args=["import random; import sys; exit_code = random.choice([0, 1, 1]); sys.exit(exit_code)"],
        retry_strategy=RetryStrategy(limit="10"),
    )
