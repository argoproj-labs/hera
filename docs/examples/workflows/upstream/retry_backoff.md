# Retry Backoff

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/retry-backoff.yaml).

# This example demonstrates the use of retry back offs
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: retry-backoff-
spec:
  entrypoint: retry-backoff
  templates:
  - name: retry-backoff
    retryStrategy:
      limit: "10"
      backoff:
        duration: "1"       # Must be a string. Default unit is seconds. Could also be a Duration, e.g.: "2m", "6h"
        factor: "2"
        maxDuration: "1m" # Must be a string. Default unit is seconds. Could also be a Duration, e.g.: "2m", "6h"
    container:
      image: python:alpine3.6
      command: ["python", -c]
      # fail with a 66% probability
      args: ["import random; import sys; exit_code = random.choice([0, 1, 1]); sys.exit(exit_code)"]


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
      - container:
          args:
          - import random; import sys; exit_code = random.choice([0, 1, 1]); sys.exit(exit_code)
          command:
          - python
          - -c
          image: python:alpine3.6
        name: retry-backoff
        retryStrategy:
          backoff:
            duration: '1'
            factor: '2'
            maxDuration: 1m
          limit: '10'
    ```

