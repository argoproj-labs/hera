from hera import Parameter, Task, Workflow, WorkflowService


def produce():
    with open("/test.txt", "w") as f:
        f.write("Hello, world!")


def consume(msg: str):
    print(f"Message was: {msg}")


ws = WorkflowService(host="https://my-argo-server.com", token="my-auth-token")

with Workflow("io", service=ws) as w:
    t1 = Task("p", produce, outputs=[Parameter("msg", value_from=dict(path="/test.txt"))])
    t2 = Task("c", consume, inputs=[t1.get_output("msg")])
    t1 >> t2

w.create()
