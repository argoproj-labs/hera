# Workflow Template  Workflow Archive Logs

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/workflow-template/workflow-archive-logs.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Workflow

    with Workflow(
        generate_name="archive-location-",
        entrypoint="hello-world",
        archive_logs=True,
    ) as w:
        Container(
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
      generateName: archive-location-
    spec:
      archiveLogs: true
      entrypoint: hello-world
      templates:
      - name: hello-world
        container:
          image: busybox
          args:
          - hello world
          command:
          - echo
    ```

