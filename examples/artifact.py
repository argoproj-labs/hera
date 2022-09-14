"""This example showcases a simple artifact passing mechanism between two tasks.

The first task, t1, creates a file located at `/file` containing a message. The second
task, t2, takes this artifact, places it at its own `/file` path, and print out the content.
"""

from hera import Artifact, Task, Workflow


def writer():
    with open("/file", "w+") as f:
        f.write("Hello, world!")


def consumer():
    with open("/file", "r") as f:
        print(f.readlines())  # prints `Hello, world!` to `stdout`


# assumes you used `hera.set_global_token` and `hera.set_global_host` so that the workflow can be submitted
with Workflow("artifact") as w:
    w_t = Task("writer", writer, outputs=[Artifact("test", "/file")])
    c_t = Task(
        "consumer",
        consumer,
        inputs=[w_t.get_output("test")],
    )

    w_t >> c_t

w.create()
