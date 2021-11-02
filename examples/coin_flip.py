"""This example showcases the classic conditional workflow coin-flip."""
from hera.v1.task import Task
from hera.v1.workflow import Workflow
from hera.v1.workflow_service import WorkflowService


def random_code():
    import random

    res = "heads" if random.randint(0, 1) == 0 else "tails"
    print(res)


def heads():
    print("it was heads")


def tails():
    print("it was tails")


# TODO: replace the domain and token with your own
ws = WorkflowService('my-argo-server.com', 'my-auth-token')
w = Workflow("coin-flip", ws)
r = Task("r", random_code)
h = Task("h", heads)
t = Task("t", tails)

r.next_when("{{item.outputs.result}} == 'heads'", h)
r.next_when("{{item.outputs.result}} == 'tails'", t)

w.add_tasks(r, h, t)
w.submit()
