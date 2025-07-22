# Gc Ttl

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/gc-ttl.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Workflow
    from hera.workflows.models import TTLStrategy

    with Workflow(
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        generate_name="gc-ttl-",
        entrypoint="hello-world",
        ttl_strategy=TTLStrategy(
            seconds_after_completion=10,
            seconds_after_failure=5,
            seconds_after_success=5,
        ),
    ) as w:
        Container(
            name="hello-world",
            args=["hello world"],
            command=["echo"],
            image="busybox",
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: gc-ttl-
    spec:
      entrypoint: hello-world
      templates:
      - name: hello-world
        container:
          image: busybox
          args:
          - hello world
          command:
          - echo
      ttlStrategy:
        secondsAfterCompletion: 10
        secondsAfterFailure: 5
        secondsAfterSuccess: 5
    ```

