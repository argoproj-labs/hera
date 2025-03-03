# Artifact Repository Ref

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/artifact-repository-ref.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        Artifact,
        Container,
        Workflow,
        models as m,
    )

    with Workflow(
        generate_name="artifact-repository-ref-",
        entrypoint="main",
        artifact_repository_ref=m.ArtifactRepositoryRef(key="my-key"),
    ) as w:
        Container(
            name="main",
            image="busybox",
            command=["sh", "-c"],
            args=["echo hello world | tee /tmp/hello_world.txt"],
            outputs=[Artifact(name="hello_world", path="/tmp/hello_world.txt")],
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: artifact-repository-ref-
    spec:
      entrypoint: main
      templates:
      - name: main
        container:
          image: busybox
          args:
          - echo hello world | tee /tmp/hello_world.txt
          command:
          - sh
          - -c
        outputs:
          artifacts:
          - name: hello_world
            path: /tmp/hello_world.txt
      artifactRepositoryRef:
        key: my-key
    ```

