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
    whalesay = Container(
        name="whalesay",
        image="docker/whalesay:latest",
        command=["sh", "-c"],
        args=["cowsay hello world | tee /tmp/hello_world.txt | tee /tmp/hello_world_nc.txt ; sleep 1"],
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
    print_message = Container(
        name="print-message",
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
        step = Step(name="generate-artifact", template=whalesay)
        Step(
            name="consume-artifact",
            template=print_message,
            arguments=[
                Artifact(name="etc", from_=step.outputs.artifacts.etc),
                Artifact(name="hello-txt", from_=step.outputs.artifacts.hello_txt),
                Artifact(name="hello-txt-nc", from_=step.outputs.artifacts.hello_txt_nc),
            ],
        )
