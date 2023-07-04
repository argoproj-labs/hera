# Input Artifact Gcs

> Note: This example is a replication of an Argo Workflow example in Hera. 




=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        Container,
        GCSArtifact,
        Workflow,
        models as m,
    )

    with Workflow(generate_name="input-artifact-gcs-", entrypoint="input-artifact-gcs-example") as w:
        Container(
            name="input-artifact-gcs-example",
            image="debian:latest",
            command=["sh", "-c"],
            args=["ls -l /my-artifact"],
            inputs=[
                GCSArtifact(
                    name="my-art",
                    path="/my-artifact",
                    bucket="my-bucket-name",
                    key="path/in/bucket",
                    service_account_key_secret=m.SecretKeySelector(
                        name="my-gcs-credentials",
                        key="serviceAccountKey",
                    ),
                ),
            ],
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: input-artifact-gcs-
    spec:
      entrypoint: input-artifact-gcs-example
      templates:
      - container:
          args:
          - ls -l /my-artifact
          command:
          - sh
          - -c
          image: debian:latest
        inputs:
          artifacts:
          - gcs:
              bucket: my-bucket-name
              key: path/in/bucket
              serviceAccountKeySecret:
                key: serviceAccountKey
                name: my-gcs-credentials
            name: my-art
            path: /my-artifact
        name: input-artifact-gcs-example
    ```

