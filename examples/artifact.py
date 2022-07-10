"""This example showcases a simple artifact passing mechanism between two tasks.

The first task, t1, creates a file located at `/file` containing a message. The second
task, t2, takes this artifact, places it at its own `/file` path, and print out the content.
"""

from hera import InputArtifact, OutputArtifact, Task, Workflow, WorkflowService


def writer():
    with open("/file", "w+") as f:
        f.write("Hello, world!")


def consumer():
    with open("/file", "r") as f:
        print(f.readlines())  # prints `Hello, world!` to `stdout`


with Workflow("artifact", service=WorkflowService(host="https://my-argo-server.com", token="my-auth-token")) as w:
    w_t = Task("writer", writer, output_artifacts=[OutputArtifact("test", "/file")])
    c_t = Task(
        "consumer",
        consumer,
        input_artifacts=[InputArtifact("test", "/file", "writer", "test")],
    )

    w_t >> c_t

w.create()
