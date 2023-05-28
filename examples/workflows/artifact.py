"""This example showcases a simple artifact passing mechanism between two tasks.
The first task, writer, creates a file located at `/file` containing a message. The second
task, consumer, takes this artifact, places it at its own `/file` path, and print out the content.
"""

from hera.workflows import DAG, Artifact, Workflow, script


@script(outputs=Artifact(name="test", path="/file"))
def writer():
    with open("/file", "w+") as f:
        f.write("Hello, world!")


@script(inputs=Artifact(name="test", path="/file"))
def consumer():
    with open("/file", "r") as f:
        print(f.readlines())  # prints `Hello, world!` to `stdout`


with Workflow(generate_name="artifact-", entrypoint="d") as w:
    with DAG(name="d"):
        w_ = writer()
        c = consumer(arguments={"test": w_.get_artifact("test")})
        w_ >> c
