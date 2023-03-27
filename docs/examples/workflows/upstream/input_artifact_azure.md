# Input Artifact Azure

> Note: This example is a replication of an Argo Workflow example in Hera. The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/input-artifact-azure.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        AzureArtifact,
        Container,
        Workflow,
        models as m,
    )

    # the example is accidentally named input-artifact-s3-... upstream, keeping here for testing/consistency. Note that
    # the Azure artifact is set correctly
    with Workflow(generate_name="input-artifact-s3-", entrypoint="input-artifact-s3-example") as w:
        Container(
            name="input-artifact-s3-example",
            image="debian:latest",
            command=["sh", "-c"],
            args=["ls -l /my-artifact"],
            inputs=[
                AzureArtifact(
                    name="my-art",
                    path="/my-artifact",
                    endpoint="https://myazurestorageaccountname.blob.core.windows.net",
                    container="my-container",
                    blob="path/in/container",
                    account_key_secret=m.SecretKeySelector(
                        name="my-azure-credentials",
                        key="accountKey",
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
          - azure:
              accountKeySecret:
                key: accountKey
                name: my-azure-credentials
              blob: path/in/container
              container: my-container
              endpoint: https://myazurestorageaccountname.blob.core.windows.net
            name: my-art
            path: /my-artifact
        name: input-artifact-s3-example
    ```

