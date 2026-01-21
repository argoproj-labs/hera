# Retry On Error

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/retry-on-error.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Workflow
    from hera.workflows.models import IntOrString, RetryStrategy

    with Workflow(
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        generate_name="retry-on-error-",
        entrypoint="error-container",
    ) as w:
        Container(
            name="error-container",
            retry_strategy=RetryStrategy(
                limit=IntOrString(
                    root="2",
                ),
                retry_policy="Always",
            ),
            args=["import random; import sys; exit_code = random.choice(range(0, 5)); sys.exit(exit_code)"],
            command=["python", "-c"],
            image="python",
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: retry-on-error-
    spec:
      entrypoint: error-container
      templates:
      - name: error-container
        container:
          image: python
          args:
          - import random; import sys; exit_code = random.choice(range(0, 5)); sys.exit(exit_code)
          command:
          - python
          - -c
        retryStrategy:
          limit: '2'
          retryPolicy: Always
    ```

