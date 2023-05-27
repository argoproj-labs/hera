from hera.workflows import Artifact, Steps, Workflow, script


@script(outputs=Artifact(name="hello-art", path="/tmp/hello_world.txt"))
def whalesay():
    with open("/tmp/hello_world.txt", "wb") as f:
        f.write("hello world")


@script(inputs=Artifact(name="message", path="/tmp/message"))
def print_message():
    with open("//tmp/message", "rb") as f:
        message = f.readline()
    print(message)


with Workflow(generate_name="artifact-passing-", entrypoint="artifact-example") as w:
    with Steps(name="artifact-example") as s:
        ga = whalesay(name="generate-artifact")
        print_message(name="consume-artifact", message=ga.get_artifact("hello-art"))
