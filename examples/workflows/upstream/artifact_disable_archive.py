from hera.workflows import (
    Artifact,
    Container,
    Step,
    Steps,
    Workflow,
    models as m,
)

with Workflow(generate_name="artifact-disable-archive-", entrypoint="artifact-disable-archive") as w:
    whalesay = Container(
        name="whalesay",
        image="docker/whalesay:latest",
        command=["sh", "-c"],
        args=["cowsay hello world | tee /tmp/hello_world.txt | tee /tmp/hello_world_nc.txt ; sleep 1"],
        outputs=[
            Artifact(name="etc", path="/etc", archive=m.ArchiveStrategy(none=m.NoneStrategy())),
            Artifact(name="hello-txt", path="/tmp/hello_world.txt", archive=m.ArchiveStrategy(none=m.NoneStrategy())),
            Artifact(
                name="hello-txt-nc",
                path="/tmp/hello_world_nc.txt",
                archive=m.ArchiveStrategy(tar=m.TarStrategy(compression_level=0)),
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
        Step(name="generate-artifact", template=whalesay)
        Step(
            name="consume-artifact",
            template=print_message,
            arguments=[
                Artifact(name="etc", from_="{{steps.generate-artifact.outputs.artifacts.etc}}"),
                Artifact(name="hello-txt", from_="{{steps.generate-artifact.outputs.artifacts.hello-txt}}"),
                Artifact(name="hello-txt-nc", from_="{{steps.generate-artifact.outputs.artifacts.hello-txt-nc}}"),
            ],
        )
