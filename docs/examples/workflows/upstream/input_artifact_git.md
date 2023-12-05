# Input Artifact Git

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/input-artifact-git.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        Container,
        GitArtifact,
        Workflow,
    )

    with Workflow(generate_name="input-artifact-git-", entrypoint="git-clone") as w:
        Container(
            name="git-clone",
            image="golang:1.10",
            command=["sh", "-c"],
            args=["git status && ls && cat VERSION"],
            working_dir="/src",
            inputs=[
                GitArtifact(
                    name="argo-source",
                    path="/src",
                    repo="https://github.com/argoproj/argo-workflows.git",
                    revision="v2.1.1",
                ),
            ],
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: input-artifact-git-
    spec:
      entrypoint: git-clone
      templates:
      - container:
          args:
          - git status && ls && cat VERSION
          command:
          - sh
          - -c
          image: golang:1.10
          workingDir: /src
        inputs:
          artifacts:
          - git:
              repo: https://github.com/argoproj/argo-workflows.git
              revision: v2.1.1
            name: argo-source
            path: /src
        name: git-clone
    ```

