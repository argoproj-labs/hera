# Timeouts Step

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/timeouts-step.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Workflow

    with Workflow(
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        generate_name="timeouts-step-",
        entrypoint="sleep",
    ) as w:
        Container(
            active_deadline_seconds=10,
            name="sleep",
            args=["echo 123; sleep 1d"],
            command=["bash", "-c"],
            image="argoproj/argosay:v2",
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: timeouts-step-
    spec:
      entrypoint: sleep
      templates:
      - name: sleep
        activeDeadlineSeconds: 10
        container:
          image: argoproj/argosay:v2
          args:
          - echo 123; sleep 1d
          command:
          - bash
          - -c
    ```

