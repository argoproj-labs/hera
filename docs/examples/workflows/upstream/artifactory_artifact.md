# Artifactory Artifact

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/artifactory-artifact.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        Artifact,
        ArtifactoryArtifact,
        Container,
        Step,
        Steps,
        Workflow,
        models as m,
    )

    with Workflow(generate_name="artifactory-artifact-", entrypoint="artifact-example") as w:
        hello_world_to_file = Container(
            name="hello-world-to-file",
            image="busybox",
            command=["sh", "-c"],
            args=["echo hello world | tee /tmp/hello_world.txt"],
            outputs=[
                ArtifactoryArtifact(
                    name="hello-art",
                    path="/tmp/hello_world.txt",
                    url="http://artifactory:8081/artifactory/generic-local/hello_world.tgz",
                    username_secret=m.SecretKeySelector(name="my-artifactory-credentials", key="username"),
                    password_secret=m.SecretKeySelector(name="my-artifactory-credentials", key="password"),
                )
            ],
        )
        print_message_from_file = Container(
            name="print-message-from-file",
            image="alpine:latest",
            command=["sh", "-c"],
            args=["cat /tmp/message"],
            inputs=[
                ArtifactoryArtifact(
                    name="message",
                    path="/tmp/message",
                    url="http://artifactory:8081/artifactory/generic-local/hello_world.tgz",
                    username_secret=m.SecretKeySelector(name="my-artifactory-credentials", key="username"),
                    password_secret=m.SecretKeySelector(name="my-artifactory-credentials", key="password"),
                )
            ],
        )

        with Steps(name="artifact-example") as s:
            Step(name="generate-artifact", template=hello_world_to_file)
            Step(
                name="consume-artifact",
                template=print_message_from_file,
                arguments=[Artifact(name="message", from_="{{steps.generate-artifact.outputs.artifacts.hello-art}}")],
            )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: artifactory-artifact-
    spec:
      entrypoint: artifact-example
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
          - artifactory:
              passwordSecret:
                key: password
                name: my-artifactory-credentials
              url: http://artifactory:8081/artifactory/generic-local/hello_world.tgz
              usernameSecret:
                key: username
                name: my-artifactory-credentials
            name: hello-art
            path: /tmp/hello_world.txt
      - container:
          args:
          - cat /tmp/message
          command:
          - sh
          - -c
          image: alpine:latest
        inputs:
          artifacts:
          - artifactory:
              passwordSecret:
                key: password
                name: my-artifactory-credentials
              url: http://artifactory:8081/artifactory/generic-local/hello_world.tgz
              usernameSecret:
                key: username
                name: my-artifactory-credentials
            name: message
            path: /tmp/message
        name: print-message-from-file
      - name: artifact-example
        steps:
        - - name: generate-artifact
            template: hello-world-to-file
        - - arguments:
              artifacts:
              - from: '{{steps.generate-artifact.outputs.artifacts.hello-art}}'
                name: message
            name: consume-artifact
            template: print-message-from-file
    ```

