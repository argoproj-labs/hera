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
