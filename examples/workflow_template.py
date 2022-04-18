"""This example showcases the classic conditional workflow coin-flip."""
from hera.operator import Operator
from hera.task import Task
from hera.workflow import Workflow
from hera.workflow_service import WorkflowService
from hera.workflow_template import WorkflowTemplate
from hera.workflow_template_service import WorkflowTemplateService


def random_code():
    import random

    res = "heads" if random.randint(0, 1) == 0 else "tails"
    print(res)


def heads():
    print("it was heads")


def tails():
    print("it was tails")


# TODO: replace the domain and token with your own
wts = WorkflowTemplateService(host='', verify_ssl=False, token="", namespace="argo")
w = WorkflowTemplate("workflow-template", wts, namespace="argo")
r = Task("r", random_code)
h = Task("h", heads)
t = Task("t", tails)

h.when(r, Operator.equals, "heads")
t.when(r, Operator.equals, "tails")

w.add_tasks(r, h, t)
w.create(namespace="argo")
