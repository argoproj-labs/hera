# Hdfs Artifact

## Note

This example is a replication of an Argo Workflow example in Hera.
The upstream example can be [found here](https://github.com/argoproj/argo-workflows/blob/main/examples/hdfs-artifact.yaml).




=== "Hera"

    ```python linenums="1"
    from hera.workflows import (
        Artifact,
        Container,
        HDFSArtifact,
        Step,
        Steps,
        Workflow,
    )

    with Workflow(generate_name="hdfs-artifact-", entrypoint="artifact-example") as w:
        hello_world_to_file = Container(
            name="hello-world-to-file",
            command=["sh", "-c"],
            args=["echo hello world | tee /tmp/hello_world.txt"],
            image="busybox",
            outputs=[
                HDFSArtifact(
                    name="hello-art",
                    path="/tmp/hello_world.txt",
                    addresses=[
                        "my-hdfs-namenode-0.my-hdfs-namenode.default.svc.cluster.local:8020",
                        "my-hdfs-namenode-1.my-hdfs-namenode.default.svc.cluster.local:8020",
                    ],
                    hdfs_path="/tmp/argo/foo",
                    hdfs_user="root",
                    force=True,
                )
            ],
        )
        print_message_from_hdfs = Container(
            name="print-message-from-hdfs",
            image="alpine:latest",
            command=["sh", "-c"],
            args=["cat /tmp/message"],
            inputs=[
                HDFSArtifact(
                    name="message",
                    path="/tmp/message",
                    addresses=[
                        "my-hdfs-namenode-0.my-hdfs-namenode.default.svc.cluster.local:8020",
                        "my-hdfs-namenode-1.my-hdfs-namenode.default.svc.cluster.local:8020",
                    ],
                    hdfs_path="/tmp/argo/foo",
                    hdfs_user="root",
                    force=True,
                )
            ],
        )

        with Steps(name="artifact-example") as s:
            Step(name="generate-artifact", template=hello_world_to_file)
            Step(
                name="consume-artifact",
                template=print_message_from_hdfs,
                arguments=[Artifact(name="message", from_="{{steps.generate-artifact.outputs.artifacts.hello-art}}")],
            )
    ```

=== "YAML"

    ```yaml linenums="1"
    apiVersion: argoproj.io/v1alpha1
    kind: Workflow
    metadata:
      generateName: hdfs-artifact-
    spec:
      entrypoint: artifact-example
      templates:
      - name: hello-world-to-file
        container:
          image: busybox
          args:
          - echo hello world | tee /tmp/hello_world.txt
          command:
          - sh
          - -c
        outputs:
          artifacts:
          - name: hello-art
            path: /tmp/hello_world.txt
            hdfs:
              force: true
              hdfsUser: root
              path: /tmp/argo/foo
              addresses:
              - my-hdfs-namenode-0.my-hdfs-namenode.default.svc.cluster.local:8020
              - my-hdfs-namenode-1.my-hdfs-namenode.default.svc.cluster.local:8020
      - name: print-message-from-hdfs
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
            hdfs:
              force: true
              hdfsUser: root
              path: /tmp/argo/foo
              addresses:
              - my-hdfs-namenode-0.my-hdfs-namenode.default.svc.cluster.local:8020
              - my-hdfs-namenode-1.my-hdfs-namenode.default.svc.cluster.local:8020
      - name: artifact-example
        steps:
        - - name: generate-artifact
            template: hello-world-to-file
        - - arguments:
              artifacts:
              - from: '{{steps.generate-artifact.outputs.artifacts.hello-art}}'
                name: message
            name: consume-artifact
            template: print-message-from-hdfs
    ```

