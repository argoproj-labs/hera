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
