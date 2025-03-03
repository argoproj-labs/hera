# Artifact Disable Archive

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/artifact-disable-archive.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        Artifact,
        Container,
        NoneArchiveStrategy,
        Step,
        Steps,
        TarArchiveStrategy,
        Workflow,
    )

    with Workflow(generate_name="artifact-disable-archive-", entrypoint="artifact-disable-archive") as w:
        hello_world_to_file = Container(
            name="hello-world-to-file",
            image="busybox",
            command=["sh", "-c"],
            args=["echo hello world | tee /tmp/hello_world.txt | tee /tmp/hello_world_nc.txt ; sleep 1"],
            outputs=[
                Artifact(name="etc", path="/etc", archive=NoneArchiveStrategy()),
                Artifact(name="hello-txt", path="/tmp/hello_world.txt", archive=NoneArchiveStrategy()),
                Artifact(
                    name="hello-txt-nc",
                    path="/tmp/hello_world_nc.txt",
                    archive=TarArchiveStrategy(compression_level=0),
                ),
            ],
        )
        print_message_from_files = Container(
            name="print-message-from-files",
            image="alpine:latest",
            command=["sh", "-c"],
            args=["cat /tmp/hello.txt && cat /tmp/hello_nc.txt && cd /tmp/etc && find ."],
            inputs=[
                Artifact(name="etc", path="/tmp/etc"),
                Artifact(name="hello-txt", path="/tmp/hello.txt"),
                Artifact(name="hello-txt-nc", path="/tmp/hello_nc.txt"),
            ],
        )
        with Steps(name="artifact-disable-archive") as s:
            Step(name="generate-artifact", template=hello_world_to_file)
            Step(
                name="consume-artifact",
                template=print_message_from_files,
                arguments=[
                    Artifact(name="etc", from_="{{steps.generate-artifact.outputs.artifacts.etc}}"),
                    Artifact(name="hello-txt", from_="{{steps.generate-artifact.outputs.artifacts.hello-txt}}"),
                    Artifact(name="hello-txt-nc", from_="{{steps.generate-artifact.outputs.artifacts.hello-txt-nc}}"),
                ],
            )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: artifact-disable-archive-
    spec:
      entrypoint: artifact-disable-archive
      templates:
      - name: hello-world-to-file
        container:
          image: busybox
          args:
          - echo hello world | tee /tmp/hello_world.txt | tee /tmp/hello_world_nc.txt
            ; sleep 1
          command:
          - sh
          - -c
        outputs:
          artifacts:
          - name: etc
            path: /etc
            archive:
              none: {}
          - name: hello-txt
            path: /tmp/hello_world.txt
            archive:
              none: {}
          - name: hello-txt-nc
            path: /tmp/hello_world_nc.txt
            archive:
              tar:
                compressionLevel: 0
      - name: print-message-from-files
        container:
          image: alpine:latest
          args:
          - cat /tmp/hello.txt && cat /tmp/hello_nc.txt && cd /tmp/etc && find .
          command:
          - sh
          - -c
        inputs:
          artifacts:
          - name: etc
            path: /tmp/etc
          - name: hello-txt
            path: /tmp/hello.txt
          - name: hello-txt-nc
            path: /tmp/hello_nc.txt
      - name: artifact-disable-archive
        steps:
        - - name: generate-artifact
            template: hello-world-to-file
        - - arguments:
              artifacts:
              - from: '{{steps.generate-artifact.outputs.artifacts.etc}}'
                name: etc
              - from: '{{steps.generate-artifact.outputs.artifacts.hello-txt}}'
                name: hello-txt
              - from: '{{steps.generate-artifact.outputs.artifacts.hello-txt-nc}}'
                name: hello-txt-nc
            name: consume-artifact
            template: print-message-from-files
    ```

