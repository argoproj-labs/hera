from hera.workflows import (
    Artifact,
    Container,
    Step,
    Steps,
    Workflow,
    models as m,
)

with Workflow(generate_name="artifact-passing-subpath-", entrypoint="artifact-example") as w:
    whalesay = Container(
        name="whalesay",
        image="docker/whalesay:latest",
        command=["sh", "-c"],
        args=["sleep 1; cowsay hello world | tee /tmp/hello_world.txt"],
        outputs=[Artifact(name="hello-art", path="/tmp/", archive=m.ArchiveStrategy(none=m.NoneStrategy()))],
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
