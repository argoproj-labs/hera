# Output Artifact Azure

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/output-artifact-azure.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        AzureArtifact,
        Container,
        Workflow,
        models as m,
    )

    with Workflow(generate_name="output-artifact-s3-", entrypoint="whalesay") as w:
        Container(
            name="whalesay",
            image="docker/whalesay:latest",
            command=["sh", "-c"],
            args=["cowsay hello world | tee /tmp/hello_world.txt"],
            outputs=[
                AzureArtifact(
                    name="message",
                    path="/tmp",
                    endpoint="https://myazurestorageaccountname.blob.core.windows.net",
                    container="my-container",
                    blob="path/in/container/hello_world.txt.tgz",
                    account_key_secret=m.SecretKeySelector(name="my-azure-credentials", key="accountKey"),
                )
            ],
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: output-artifact-s3-
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
          - azure:
              accountKeySecret:
                key: accountKey
                name: my-azure-credentials
              blob: path/in/container/hello_world.txt.tgz
              container: my-container
              endpoint: https://myazurestorageaccountname.blob.core.windows.net
            name: message
            path: /tmp
    ```

