"""This example showcases conditional execution on success, failure, and error"""
from hera import Task, Workflow, WorkflowService


def random():
    import random

    p = random.random()
    if p <= 0.5:
        raise Exception("FAILURE")
    print("SUCCESS")


def success():
    print("SUCCESS")


def failure():
    print("FAILURE")


with Workflow("conditional", service=WorkflowService(host="https://my-argo-server.com", token="my-auth-token")) as w:
    r = Task("random", random)
    s = Task("success", success)
    f = Task("failure", failure)

    r.on_success(s)
    r.on_failure(f)

w.create()
