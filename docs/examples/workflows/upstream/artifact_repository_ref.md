# Artifact Repository Ref

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/artifact-repository-ref.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        Artifact,
        Container,
        Workflow,
        models as m,
    )

    with Workflow(
        generate_name="artifactory-repository-ref-",
        entrypoint="main",
        artifact_repository_ref=m.ArtifactRepositoryRef(key="my-key"),
    ) as w:
        Container(
            name="main",
            image="docker/whalesay:latest",
            command=["sh", "-c"],
            args=["cowsay hello world | tee /tmp/hello_world.txt"],
            outputs=[Artifact(name="hello_world", path="/tmp/hello_world.txt")],
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: artifactory-repository-ref-
    spec:
      artifactRepositoryRef:
        key: my-key
      entrypoint: main
      templates:
      - container:
          args:
          - cowsay hello world | tee /tmp/hello_world.txt
          command:
          - sh
          - -c
          image: docker/whalesay:latest
        name: main
        outputs:
          artifacts:
          - name: hello_world
            path: /tmp/hello_world.txt
    ```

