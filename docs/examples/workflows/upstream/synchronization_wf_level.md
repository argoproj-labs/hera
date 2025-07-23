# Synchronization Wf Level

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/synchronization-wf-level.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Workflow
    from hera.workflows.models import ConfigMapKeySelector, SemaphoreRef, Synchronization

    with Workflow(
        api_version="argoproj.io/v1alpha1",
        kind="Workflow",
        generate_name="synchronization-wf-level-",
        entrypoint="hello-world",
        synchronization=Synchronization(
            semaphores=[
                SemaphoreRef(
                    config_map_key_ref=ConfigMapKeySelector(
                        key="workflow",
                        name="my-config",
                    ),
                )
            ],
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
        semaphores:
        - configMapKeyRef:
            name: my-config
            key: workflow
    ```

