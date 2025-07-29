# Retry Workflow



This examples uses a RetryStrategy at the Workflow level, rather than the template level.

The Workflow is functionally equivalent to the
[Retry Container To Completion](../upstream/retry_container_to_completion.md) example, but as the RetryStrategy is on
the Workflow itself, it will apply by default to *all* templates in the Workflow.


=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        Container,
        RetryStrategy,
        Workflow,
        models as m,
    )

    with Workflow(
        generate_name="retry-backoff-",
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
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: retry-backoff-
    spec:
      entrypoint: retry-backoff
      templates:
      - name: retry-backoff
        container:
          image: python:alpine3.6
          args:
          - import random; import sys; exit_code = random.choice(range(0, 5)); sys.exit(exit_code)
          command:
          - python
          - -c
      retryStrategy:
        limit: '10'
        backoff:
          duration: '1'
          factor: '2'
          maxDuration: 1m
    ```

