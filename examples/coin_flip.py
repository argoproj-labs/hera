"""This example showcases the classic conditional workflow coin-flip."""
from hera import Operator, Task, Workflow, WorkflowService


def random_code():
    import random

    res = "heads" if random.randint(0, 1) == 0 else "tails"
    print(res)


def heads():
    print("it was heads")


def tails():
    print("it was tails")


with Workflow("coin-flip", service=WorkflowService(host='https://my-argo-server.com', token='my-auth-token')) as w:
    r = Task("r", random_code)
    h = Task("h", heads)
    t = Task("t", tails)

    h.when(r, Operator.equals, "heads")
    t.when(r, Operator.equals, "tails")

w.create()
