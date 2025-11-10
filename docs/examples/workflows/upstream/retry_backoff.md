# Retry Backoff

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/retry-backoff.yaml).




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
          - import random; import sys; exit_code = random.choice([0, 1, 1]); sys.exit(exit_code)
          command:
          - python
          - -c
        retryStrategy:
          limit: '10'
          backoff:
            cap: '5'
            duration: '1'
            factor: '2'
            maxDuration: 1m
    ```

