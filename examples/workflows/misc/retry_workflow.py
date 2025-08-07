"""This examples uses a RetryStrategy at the Workflow level, rather than the template level.

The Workflow is functionally equivalent to the
[Retry Container To Completion](../upstream/retry_container_to_completion.md) example, but as the RetryStrategy is on
the Workflow itself, it will apply by default to *all* templates in the Workflow.
"""

from hera.workflows import (
    Container,
    RetryStrategy,
    Workflow,
    models as m,
)

with Workflow(
    generate_name="retry-workflow-",
    entrypoint="retry-backoff",
    retry_strategy=RetryStrategy(
        limit="10",
        backoff=m.Backoff(
            duration="1",
            factor="2",
            max_duration="1m",
        ),
    ),
) as w:
    retry_backoff = Container(
        name="retry-backoff",
        image="python:alpine3.6",
        command=["python", "-c"],
        args=["import random; import sys; exit_code = random.choice(range(0, 5)); sys.exit(exit_code)"],
    )
