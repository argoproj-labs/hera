# Artifact Passing Subpath

> Note: This example is a replication of an Argo Workflow example in Hera. The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/master/examples/artifact-passing-subpath.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        Artifact,
        Container,
        NoneArchiveStrategy,
        Step,
        Steps,
        Workflow,
    )

    with Workflow(generate_name="artifact-passing-subpath-", entrypoint="artifact-example") as w:
        whalesay = Container(
            name="whalesay",
            image="docker/whalesay:latest",
            command=["sh", "-c"],
            args=["sleep 1; cowsay hello world | tee /tmp/hello_world.txt"],
            outputs=[Artifact(name="hello-art", path="/tmp/", archive=NoneArchiveStrategy())],
        )
        print_message_dir = Container(
            name="print-message-dir",
            image="alpine:latest",
            command=["sh", "-c"],
            args=["ls /tmp/message"],
            inputs=[Artifact(name="message", path="/tmp/message")],
        )
        print_message = Container(
            name="print-message",
            image="alpine:latest",
            command=["sh", "-c"],
            args=["cat /tmp/message"],
            inputs=[Artifact(name="message", path="/tmp/message")],
        )
        with Steps(name="artifact-example") as s:
            Step(name="generate-artifact", template=whalesay)
            Step(
                name="list-artifact",
                template=print_message_dir,
                arguments=[Artifact(name="message", from_="{{steps.generate-artifact.outputs.artifacts.hello-art}}")],
            )
            Step(
                name="consume-artifact",
                template=print_message,
                arguments=[
                    Artifact(
                        name="message",
                        from_="{{steps.generate-artifact.outputs.artifacts.hello-art}}",
                        sub_path="hello_world.txt",
                    )
                ],
            )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: artifact-passing-subpath-
    spec:
      entrypoint: artifact-example
      templates:
      - container:
          args:
          - sleep 1; cowsay hello world | tee /tmp/hello_world.txt
          command:
          - sh
          - -c
          image: docker/whalesay:latest
        name: whalesay
        outputs:
          artifacts:
          - archive:
              none: {}
            name: hello-art
            path: /tmp/
      - container:
          args:
          - ls /tmp/message
          command:
          - sh
          - -c
          image: alpine:latest
        inputs:
          artifacts:
          - name: message
            path: /tmp/message
        name: print-message-dir
      - container:
          args:
          - cat /tmp/message
          command:
          - sh
          - -c
          image: alpine:latest
        inputs:
          artifacts:
          - name: message
            path: /tmp/message
        name: print-message
      - name: artifact-example
        steps:
        - - name: generate-artifact
            template: whalesay
        - - arguments:
              artifacts:
              - from: '{{steps.generate-artifact.outputs.artifacts.hello-art}}'
                name: message
            name: list-artifact
            template: print-message-dir
        - - arguments:
              artifacts:
              - from: '{{steps.generate-artifact.outputs.artifacts.hello-art}}'
                name: message
                subPath: hello_world.txt
            name: consume-artifact
            template: print-message
    ```

