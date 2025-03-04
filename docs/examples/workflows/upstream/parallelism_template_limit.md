# Parallelism Template Limit

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/parallelism-template-limit.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Steps, Workflow

    with Workflow(
        generate_name="parallelism-template-limit-",
        entrypoint="parallelism-template-limit",
    ) as w:
        sleep = Container(
            name="sleep",
            image="alpine:latest",
            command=["sh", "-c", "sleep 10"],
        )
        with Steps(name="parallelism-template-limit", parallelism=2):
            sleep(
                with_items=[
                    "this",
                    "workflow",
                    "should",
                    "take",
                    "at",
                    "least",
                    60,
                    "seconds",
                    "to",
                    "complete",
                ]
            )

    print(w.to_yaml())
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: parallelism-template-limit-
    spec:
      entrypoint: parallelism-template-limit
      templates:
      - name: sleep
        container:
          image: alpine:latest
          command:
          - sh
          - -c
          - sleep 10
      - name: parallelism-template-limit
        parallelism: 2
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

