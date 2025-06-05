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
