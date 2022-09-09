from hera import Artifact, Task, Workflow, WorkflowService


def writer():
    import json

    with open("/file", "w+") as f:
        for i in range(10):
            f.write(f"{json.dumps(i)}\n")


def fanout():
    import json
    import sys

    indices = []
    with open("/file", "r") as f:
        for line in f.readlines():
            indices.append({"i": line})
    json.dump(indices, sys.stdout)


def consumer(i: int):
    print(i)


ws = WorkflowService(host="https://my-argo-server.com", token="my-auth-token")

with Workflow("artifact-with-fanout", service=ws) as w:
    w_t = Task("writer", writer, outputs=[Artifact("test", "/file")])
    f_t = Task(
        "fanout",
        fanout,
        inputs=[w_t.get_output("test")],
    )
    c_t = Task("consumer", consumer, with_param=f_t.get_result_as("i"))
    w_t >> f_t >> c_t

w.create()
