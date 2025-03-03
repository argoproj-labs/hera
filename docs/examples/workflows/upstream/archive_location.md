# Archive Location

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/archive-location.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        Container,
        Workflow,
    )

    with Workflow(
        generate_name="archive-location-",
        entrypoint="hello-world",
    ) as w:
        Container(
            name="hello-world",
            image="busybox",
            command=["echo"],
            args=["hello world"],
            archive_location={"archive_logs": True},
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: archive-location-
    spec:
      entrypoint: hello-world
      templates:
      - name: hello-world
        archiveLocation:
          archiveLogs: true
        container:
          image: busybox
          args:
          - hello world
          command:
          - echo
    ```

