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

    with Workflow(generate_name="output-artifact-s3-", entrypoint="hello-world-to-file") as w:
        Container(
            name="hello-world-to-file",
            image="busybox",
            command=["sh", "-c"],
            args=["echo hello world | tee /tmp/hello_world.txt"],
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
      entrypoint: hello-world-to-file
      templates:
      - container:
          args:
          - echo hello world | tee /tmp/hello_world.txt
          command:
          - sh
          - -c
          image: busybox
        name: hello-world-to-file
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

