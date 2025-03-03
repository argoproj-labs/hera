# Synchronization Wf Level Legacy

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/synchronization-wf-level-legacy.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        Container,
        Workflow,
        models as m,
    )

    with Workflow(
        generate_name="synchronization-wf-level-",
        entrypoint="hello-world",
        synchronization=m.Synchronization(
            semaphore=m.SemaphoreRef(
                config_map_key_ref=m.ConfigMapKeySelector(
                    name="my-config",
                    key="workflow",
                )
            )
        ),
    ) as w:
        hello_world = Container(
            name="hello-world",
            image="busybox",
            command=["echo"],
            args=["hello world"],
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: synchronization-wf-level-
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
      synchronization:
        semaphore:
          configMapKeyRef:
            name: my-config
            key: workflow
    ```

