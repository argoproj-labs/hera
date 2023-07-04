# Parallelism Limit

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/parallelism-limit.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Steps, Workflow

    with Workflow(
        generate_name="parallelism-limit-",
        entrypoint="parallelism-limit",
        parallelism=2,
    ) as w:
        sleep = Container(
            name="sleep",
            image="alpine:latest",
            command=["sh", "-c", "sleep 10"],
        )

        with Steps(name="parallelism-limit") as steps:
            sleep(with_items=["this", "workflow", "should", "take", "at", "least", 60, "seconds", "to", "complete"])
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: parallelism-limit-
    spec:
      entrypoint: parallelism-limit
      parallelism: 2
      templates:
      - container:
          command:
          - sh
          - -c
          - sleep 10
          image: alpine:latest
        name: sleep
      - name: parallelism-limit
        steps:
        - - name: sleep
            template: sleep
            withItems:
            - this
            - workflow
            - should
            - take
            - at
            - least
            - 60
            - seconds
            - to
            - complete
    ```

