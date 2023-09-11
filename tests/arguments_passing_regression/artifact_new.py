"""This example showcases a simple artifact passing mechanism between two tasks.
The first task, writer, creates a file located at `/file` containing a message. The second
task, consumer, takes this artifact, places it at its own `/file` path, and print out the content.
"""

from hera.workflows import DAG, Artifact, NoneArchiveStrategy, Workflow, script


@script(outputs=Artifact(name="out-art", path="/tmp/file", archive=NoneArchiveStrategy()))
def writer():
    with open("/tmp/file", "w+") as f:
        f.write("Hello, world!")


@script(inputs=Artifact(name="in-art", path="/tmp/file"), use_func_params_in_call=True)
def consumer():
    with open("/tmp/file", "r") as f:
        print(f.readlines())  # prints `Hello, world!` to `stdout`


with Workflow(generate_name="artifact-", entrypoint="d") as w:
    with DAG(name="d"):
        w_ = writer()
        c = consumer(w_.get_artifact("out-art").as_name("in-art"))
        w_ >> c
