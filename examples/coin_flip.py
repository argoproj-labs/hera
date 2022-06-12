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


# TODO: replace the domain and token with your own
ws = WorkflowService(host='https://my-argo-server.com', token='my-auth-token')
w = Workflow("coin-flip", ws)
r = Task("r", random_code)
h = Task("h", heads)
t = Task("t", tails)

h.when(r, Operator.equals, "heads")
t.when(r, Operator.equals, "tails")

w.add_tasks(r, h, t)
w.create()
