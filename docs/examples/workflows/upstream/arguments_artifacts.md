# Arguments Artifacts

> Note: This example is a replication of an Argo Workflow example in Hera. The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/arguments-artifacts.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Artifact, Container, HTTPArtifact, Workflow

    with Workflow(
        generate_name="arguments-artifacts-",
        entrypoint="kubectl-input-artifact",
        arguments=[
            HTTPArtifact(
                name="kubectl",
                url="https://storage.googleapis.com/kubernetes-release/release/v1.8.0/bin/linux/amd64/kubectl",
            ),
        ],
    ) as w:
        Container(
            name="kubectl-input-artifact",
            image="debian:9.4",
            command=["sh", "-c"],
            args=["kubectl version"],
            inputs=[Artifact(name="kubectl", path="/usr/local/bin/kubectl", mode=493)],
        )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: arguments-artifacts-
    spec:
      arguments:
        artifacts:
        - http:
            url: https://storage.googleapis.com/kubernetes-release/release/v1.8.0/bin/linux/amd64/kubectl
          name: kubectl
      entrypoint: kubectl-input-artifact
      templates:
      - container:
          args:
          - kubectl version
          command:
          - sh
          - -c
          image: debian:9.4
        inputs:
          artifacts:
          - mode: 493
            name: kubectl
            path: /usr/local/bin/kubectl
        name: kubectl-input-artifact
    ```

