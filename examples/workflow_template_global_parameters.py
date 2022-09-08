from hera import (
    GlobalInputParameter,
    Task,
    Variable,
    WorkflowTemplate,
    WorkflowTemplateService,
)


def foo(v):
    print(v)


with WorkflowTemplate(
    "global-parameters",
    service=WorkflowTemplateService(host="my-argo-server.com", token="my-token"),
    variables=[Variable("v", "42")],
) as w:
    Task("t", foo, inputs=[GlobalInputParameter("v", "v")])

w.create()
