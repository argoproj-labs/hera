# Output Artifact Gcs

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/output-artifact-gcs.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        Container,
        GCSArtifact,
        Workflow,
        models as m,
    )

    with Workflow(generate_name="output-artifact-gcs-", entrypoint="whalesay") as w:
        Container(
            name="whalesay",
            image="docker/whalesay:latest",
            command=["sh", "-c"],
            args=["cowsay hello world | tee /tmp/hello_world.txt"],
            outputs=[
                GCSArtifact(
                    name="message",
                    path="/tmp",
                    bucket="my-bucket",
                    key="path/in/bucket/hello_world.txt.tgz",
                    service_account_key_secret=m.SecretKeySelector(name="my-gcs-credentials", key="serviceAccountKey"),
                )
            ],
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: output-artifact-gcs-
    spec:
      entrypoint: whalesay
      templates:
      - container:
          args:
          - cowsay hello world | tee /tmp/hello_world.txt
          command:
          - sh
          - -c
          image: docker/whalesay:latest
        name: whalesay
        outputs:
          artifacts:
          - gcs:
              bucket: my-bucket
              key: path/in/bucket/hello_world.txt.tgz
              serviceAccountKeySecret:
                key: serviceAccountKey
                name: my-gcs-credentials
            name: message
            path: /tmp
    ```

