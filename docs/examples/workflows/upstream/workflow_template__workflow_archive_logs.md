# Workflow Template  Workflow Archive Logs

> Note: This example is a replication of an Argo Workflow example in Hera. 




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, Workflow

    with Workflow(
        generate_name="archive-location-",
        entrypoint="whalesay",
        archive_logs=True,
    ) as w:
        Container(
            name="whalesay",
            image="docker/whalesay:latest",
            command=["cowsay"],
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
      entrypoint: whalesay
      templates:
      - container:
          args:
          - hello world
          command:
          - cowsay
          image: docker/whalesay:latest
        name: whalesay
    ```

