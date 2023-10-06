from hera.workflows import Artifact, Container, Step, Steps, Workflow

with Workflow(generate_name="artifact-passing-", entrypoint="artifact-example") as w:
    whalesay = Container(
        name="whalesay",
        image="docker/whalesay:latest",
        command=["sh", "-c"],
        args=["sleep 1; cowsay hello world | tee /tmp/hello_world.txt"],
        outputs=[Artifact(name="hello-art", path="/tmp/hello_world.txt")],
    )
    print_message = Container(
        name="print-message",
        image="alpine:latest",
        command=["sh", "-c"],
        args=["cat /tmp/message"],
        inputs=[Artifact(name="message", path="/tmp/message")],
    )

    with Steps(name="artifact-example") as s:
        gen_step = Step(name="generate-artifact", template=whalesay)
        Step(
            name="consume-artifact",
            template=print_message,
            arguments=gen_step.get_artifact("hello-art").with_name("message"),
        )
