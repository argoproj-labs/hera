from hera import (
    InputParameter,
    Memoize,
    OutputPathParameter,
    Task,
    Workflow,
    WorkflowService,
)


def generate():
    with open("/out", "w") as f:
        f.write("42")


def consume(value):
    print(f"Received value: {value}")


with Workflow("memoize", service=WorkflowService(host="my-argo-server.com", token="my-token")) as w:
    g = Task("g", generate, outputs=[OutputPathParameter("out", "/out")])
    c = Task("c", consume, inputs=[InputParameter("value", g.name, "out")], memoize=Memoize("value", "memoize", "c"))
    g >> c

w.create()
