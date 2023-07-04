# Parallelism Template Limit

> Note: This example is a replication of an Argo Workflow example in Hera. 




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
      - container:
          command:
          - sh
          - -c
          - sleep 10
          image: alpine:latest
        name: sleep
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

