from hera import Parameter, Task, Workflow, WorkflowService


def foo(v):
    print(v)


ws = WorkflowService(host="my-argo-server.com", token="my-token")

with Workflow(
    "global-parameters",
    service=ws,
    parameters=[Parameter("v", "42")],
) as w:
    Task("t", foo, inputs=[w.get_parameter("v")])

w.create()
