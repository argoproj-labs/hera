# Input Artifact S3

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/input-artifact-s3.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        Container,
        S3Artifact,
        Workflow,
        models as m,
    )

    with Workflow(generate_name="input-artifact-s3-", entrypoint="input-artifact-s3-example") as w:
        Container(
            name="input-artifact-s3-example",
            image="debian:latest",
            command=["sh", "-c"],
            args=["ls -l /my-artifact"],
            inputs=[
                S3Artifact(
                    name="my-art",
                    path="/my-artifact",
                    endpoint="s3.amazonaws.com",
                    bucket="my-bucket-name",
                    key="path/in/bucket",
                    region="us-west-2",
                    access_key_secret=m.SecretKeySelector(
                        name="my-s3-credentials",
                        key="accessKey",
                    ),
                    secret_key_secret=m.SecretKeySelector(
                        name="my-s3-credentials",
                        key="secretKey",
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
      generateName: input-artifact-s3-
    spec:
      entrypoint: input-artifact-s3-example
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
          - name: my-art
            path: /my-artifact
            s3:
              accessKeySecret:
                key: accessKey
                name: my-s3-credentials
              bucket: my-bucket-name
              endpoint: s3.amazonaws.com
              key: path/in/bucket
              region: us-west-2
              secretKeySecret:
                key: secretKey
                name: my-s3-credentials
        name: input-artifact-s3-example
    ```

