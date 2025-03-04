# Input Artifact Raw

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/input-artifact-raw.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Container, RawArtifact, Workflow

    with Workflow(generate_name="input-artifact-raw-", entrypoint="raw-contents") as w:
        Container(
            name="raw-contents",
            image="alpine:latest",
            command=["sh", "-c"],
            args=["cat /tmp/file"],
            inputs=[
                RawArtifact(
                    name="myfile",
                    path="/tmp/file",
                    data="this is\nthe raw file\ncontents\n",
                )
            ],
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: input-artifact-raw-
    spec:
      entrypoint: raw-contents
      templates:
      - name: raw-contents
        container:
          image: alpine:latest
          args:
          - cat /tmp/file
          command:
          - sh
          - -c
        inputs:
          artifacts:
          - name: myfile
            path: /tmp/file
            raw:
              data: |
                this is
                the raw file
                contents
    ```

