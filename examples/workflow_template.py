"""This example showcases the classic conditional workflow coin-flip."""

from hera import Operator, Task, WorkflowTemplate, WorkflowTemplateService


def random_code():
    import random

    res = "heads" if random.randint(0, 1) == 0 else "tails"
    print(res)


def heads():
    print("it was heads")


def tails():
    print("it was tails")


with WorkflowTemplate(
    "workflow-template", service=WorkflowTemplateService(host='my-argo-server.com', token='my-argo-token')
) as w:
    r = Task("r", random_code)
    Task("h", heads).when(r, Operator.equals, "heads")
    Task("t", tails).when(r, Operator.equals, "tails")

w.create()
