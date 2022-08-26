from hera import Memoize, Parameter, Task, Workflow, WorkflowService


def generate():
    with open("/out", "w") as f:
        f.write("42")


def consume(value):
    print(f"Received value: {value}")


with Workflow("memoize", service=WorkflowService(host="my-argo-server.com", token="my-token")) as w:
    g = Task("g", generate, outputs=[Parameter("out", value_from=dict(path="/out"))])
    c = Task("c", consume, inputs=[g.get_output("out")], memoize=Memoize("value", "memoize", "c"))
    g >> c

w.create()
