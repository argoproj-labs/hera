# Archive Location

> Note: This example is a replication of an Argo Workflow example in Hera. The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/archive-location.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        Container,
        Workflow,
        models as m,
    )

    with Workflow(
        generate_name="archive-location-",
        entrypoint="whalesay",
    ) as w:
        Container(
            name="whalesay",
            image="docker/whalesay:latest",
            command=["cowsay"],
            args=["hello world"],
            archive_location=m.ArtifactLocation(archive_logs=True),
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: archive-location-
    spec:
      entrypoint: whalesay
      templates:
      - archiveLocation:
          archiveLogs: true
        container:
          args:
          - hello world
          command:
          - cowsay
          image: docker/whalesay:latest
        name: whalesay
    ```

