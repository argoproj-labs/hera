# Data






=== "Hera"

    ```python linenums="1"
    from hera.expr import g, it
    from hera.workflows import (
        Artifact,
        Data,
        S3Artifact,
        Workflow,
    )

    with Workflow(generate_name="data-", entrypoint="list-log-files") as w:
        Data(
            name="list-log-files",
            source=S3Artifact(name="test-bucket", bucket="my-bucket"),
            transformations=[g.data.filter(it.ends_with("main.log"))],  # type: ignore
            outputs=Artifact(name="file", path="/file"),
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: data-
    spec:
      entrypoint: list-log-files
      templates:
      - name: list-log-files
        data:
          transformation:
          - expression: filter(data, {# endsWith 'main.log'})
          source:
            artifactPaths:
              name: test-bucket
              s3:
                bucket: my-bucket
        outputs:
          artifacts:
          - name: file
            path: /file
    ```

