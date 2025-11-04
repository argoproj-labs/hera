from hera.workflows import (
    Container,
    RetryStrategy,
    Workflow,
    models as m,
)

with Workflow(
    generate_name="retry-backoff-",
    entrypoint="retry-backoff",
) as w:
    retry_backoff = Container(
        name="retry-backoff",
        image="python:alpine3.6",
        command=["python", "-c"],
        args=["import random; import sys; exit_code = random.choice([0, 1, 1]); sys.exit(exit_code)"],
        retry_strategy=RetryStrategy(
            limit="10",
            backoff=m.Backoff(
                duration="1",
                factor="2",
                max_duration="1m",
                cap="5",
            ),
        ),
    )
