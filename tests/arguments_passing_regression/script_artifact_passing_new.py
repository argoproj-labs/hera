from hera.workflows import Artifact, Steps, Workflow, script


@script(outputs=Artifact(name="hello-art", path="/tmp/hello_world.txt"), directly_callable=True)
def whalesay():
    with open("/tmp/hello_world.txt", "w") as f:
        f.write("hello world")


@script(inputs=Artifact(name="message", path="/tmp/message"), directly_callable=True)
def print_message():
    with open("/tmp/message", "r") as f:
        message = f.readline()
    print(message)


with Workflow(generate_name="artifact-passing-", entrypoint="artifact-example") as w:
    with Steps(name="artifact-example") as s:
        whalesay().with_(name="generate-artifact")
        print_message(Artifact(name="message", from_="{{steps.generate-artifact.outputs.artifacts.hello-art}}")).with_(
            name="consume-artifact",
        )
