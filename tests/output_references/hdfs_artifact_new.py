from hera.workflows import (
    Artifact,
    Container,
    HDFSArtifact,
    Step,
    Steps,
    Workflow,
)

with Workflow(generate_name="hdfs-artifact-", entrypoint="artifact-example") as w:
    whalesay = Container(
        name="whalesay",
        command=["sh", "-c"],
        args=["cowsay hello world | tee /tmp/hello_world.txt"],
        image="docker/whalesay:latest",
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
    print_message = Container(
        name="print-message",
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
        generator = Step(name="generate-artifact", template=whalesay)
        Step(
            name="consume-artifact",
            template=print_message,
            arguments=[Artifact(name="message", from_=generator.outputs.artifacts.hello_art)],
        )
