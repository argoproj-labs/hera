from hera import GlobalInputParameter, Task, Variable, Workflow, WorkflowService


def foo(v):
    print(v)


with Workflow(
    "global-parameters",
    service=WorkflowService(host="my-argo-server.com", token="my-token"),
    variables=[Variable("v", "42")],
) as w:
    Task("t", foo, inputs=[GlobalInputParameter("v", "v")])

w.create()
