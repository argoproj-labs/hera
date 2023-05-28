# Retry Container

> Note: This example is a replication of an Argo Workflow example in Hera. The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/retry-container.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, RetryStrategy, Workflow

    with Workflow(generate_name="retry-container-", entrypoint="retry-container") as w:
        Container(
            name="retry-container",
            image="python:alpine3.6",
            command=["python", "-c"],
            args=["import random; import sys; exit_code = random.choice([0, 1, 1]); sys.exit(exit_code)"],
            retry_strategy=RetryStrategy(limit=10),
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: retry-container-
    spec:
      entrypoint: retry-container
      templates:
      - container:
          args:
          - import random; import sys; exit_code = random.choice([0, 1, 1]); sys.exit(exit_code)
          command:
          - python
          - -c
          image: python:alpine3.6
        name: retry-container
        retryStrategy:
          limit: '10'
    ```

