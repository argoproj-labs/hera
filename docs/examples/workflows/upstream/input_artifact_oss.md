# Input Artifact Oss

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/input-artifact-oss.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        Container,
        OSSArtifact,
        Workflow,
        models as m,
    )

    with Workflow(generate_name="input-artifact-oss-", entrypoint="input-artifact-oss-example") as w:
        Container(
            name="input-artifact-oss-example",
            image="debian:latest",
            command=["sh", "-c"],
            args=["ls -l /my-artifact"],
            inputs=[
                OSSArtifact(
                    name="my-art",
                    path="/my-artifact",
                    endpoint="http://oss-cn-hangzhou-zmf.aliyuncs.com",
                    bucket="test-bucket-name",
                    key="test/mydirectory/",
                    access_key_secret=m.SecretKeySelector(
                        name="my-oss-credentials",
                        key="accessKey",
                    ),
                    secret_key_secret=m.SecretKeySelector(
                        name="my-oss-credentials",
                        key="secretKey",
                    ),
                )
            ],
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: input-artifact-oss-
    spec:
      entrypoint: input-artifact-oss-example
      templates:
      - name: input-artifact-oss-example
        container:
          image: debian:latest
          args:
          - ls -l /my-artifact
          command:
          - sh
          - -c
        inputs:
          artifacts:
          - name: my-art
            path: /my-artifact
            oss:
              bucket: test-bucket-name
              endpoint: http://oss-cn-hangzhou-zmf.aliyuncs.com
              key: test/mydirectory/
              accessKeySecret:
                name: my-oss-credentials
                key: accessKey
              secretKeySecret:
                name: my-oss-credentials
                key: secretKey
    ```

