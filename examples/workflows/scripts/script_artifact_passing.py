from hera.workflows import Artifact, Steps, Workflow, script


@script(outputs=Artifact(name="hello-art", path="/tmp/hello_world.txt"))
def whalesay():
    with open("/tmp/hello_world.txt", "w") as f:
        f.write("hello world")


@script(inputs=Artifact(name="message", path="/tmp/message"))
def print_message():
    with open("/tmp/message", "r") as f:
        message = f.readline()
    print(message)


with Workflow(generate_name="artifact-passing-", entrypoint="artifact-example") as w:
    with Steps(name="artifact-example") as s:
        whale_step = whalesay(name="generate-artifact")
        print_message(
            name="consume-artifact",
            arguments=whale_step.get_artifact("hello-art").with_name("message"),
        )
