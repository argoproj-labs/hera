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
        step = whalesay(name="generate-artifact")
        print(type(step))
        print(step)
        print_message(
            name="consume-artifact",
            arguments=[Artifact(name="message", from_=step.outputs.__fields__["hello_art"])], # how to access that field directly?
        )
