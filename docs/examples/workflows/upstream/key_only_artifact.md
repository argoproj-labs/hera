# Key Only Artifact

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/key-only-artifact.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import DAG, Container, S3Artifact, Task, Workflow

    with Workflow(generate_name="key-only-artifacts-", entrypoint="main") as w:
        generate = Container(
            name="generate",
            image="argoproj/argosay:v2",
            args=["echo", "hello", "/mnt/file"],
            outputs=[
                S3Artifact(
                    name="file",
                    path="/mnt/file",
                    key="my-file",
                ),
            ],
        )
        consume = Container(
            name="consume",
            image="argoproj/argosay:v2",
            args=["cat", "/tmp/file"],
            inputs=[
                S3Artifact(
                    name="file",
                    path="/tmp/file",
                    key="my-file",
                )
            ],
        )

        with DAG(name="main"):
            Task(name="generate", template=generate) >> Task(name="consume", template=consume)
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: key-only-artifacts-
    spec:
      entrypoint: main
      templates:
      - name: generate
        container:
          image: argoproj/argosay:v2
          args:
          - echo
          - hello
          - /mnt/file
        outputs:
          artifacts:
          - name: file
            path: /mnt/file
            s3:
              key: my-file
      - name: consume
        container:
          image: argoproj/argosay:v2
          args:
          - cat
          - /tmp/file
        inputs:
          artifacts:
          - name: file
            path: /tmp/file
            s3:
              key: my-file
      - name: main
        dag:
          tasks:
          - name: generate
            template: generate
          - name: consume
            depends: generate
            template: consume
    ```

