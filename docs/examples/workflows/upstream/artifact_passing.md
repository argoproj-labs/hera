# Artifact Passing

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/artifact-passing.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import Artifact, Container, Step, Steps, Workflow

    with Workflow(generate_name="artifact-passing-", entrypoint="artifact-example") as w:
        hello_world_to_file = Container(
            name="hello-world-to-file",
            image="busybox",
            command=["sh", "-c"],
            args=["sleep 1; echo hello world | tee /tmp/hello_world.txt"],
            outputs=[Artifact(name="hello-art", path="/tmp/hello_world.txt")],
        )
        print_message_from_file = Container(
            name="print-message-from-file",
            image="alpine:latest",
            command=["sh", "-c"],
            args=["cat /tmp/message"],
            inputs=[Artifact(name="message", path="/tmp/message")],
        )

        with Steps(name="artifact-example") as s:
            gen_step = Step(name="generate-artifact", template=hello_world_to_file)
            Step(
                name="consume-artifact",
                template=print_message_from_file,
                arguments={"message": gen_step.get_artifact("hello-art")},
            )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: artifact-passing-
    spec:
      entrypoint: artifact-example
      templates:
      - name: hello-world-to-file
        container:
          image: busybox
          args:
          - sleep 1; echo hello world | tee /tmp/hello_world.txt
          command:
          - sh
          - -c
        outputs:
          artifacts:
          - name: hello-art
            path: /tmp/hello_world.txt
      - name: print-message-from-file
        container:
          image: alpine:latest
          args:
          - cat /tmp/message
          command:
          - sh
          - -c
        inputs:
          artifacts:
          - name: message
            path: /tmp/message
      - name: artifact-example
        steps:
        - - name: generate-artifact
            template: hello-world-to-file
        - - name: consume-artifact
            template: print-message-from-file
            arguments:
              artifacts:
              - name: message
                from: '{{steps.generate-artifact.outputs.artifacts.hello-art}}'
    ```

