# Retry Container To Completion

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/retry-container-to-completion.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Workflow
    from hera.workflows.models import RetryStrategy

    with Workflow(
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        generate_name="retry-to-completion-",
        entrypoint="retry-to-completion",
    ) as w:
        Container(
            name="retry-to-completion",
            retry_strategy=RetryStrategy(),
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
      generateName: retry-to-completion-
    spec:
      entrypoint: retry-to-completion
      templates:
      - name: retry-to-completion
        container:
          image: python
          args:
          - import random; import sys; exit_code = random.choice(range(0, 5)); sys.exit(exit_code)
          command:
          - python
          - -c
        retryStrategy: {}
    ```

