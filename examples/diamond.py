"""
This example showcases the classic diamond workflow that is used as an example by Argo documentation and
other libraries.
"""
from hera import Task, Workflow, WorkflowService


def say(message: str):
    print(message)


with Workflow("diamond", service=WorkflowService(host="https://my-argo-server.com", token="my-auth-token")) as w:
    a = Task("A", say, [{"message": "This is task A!"}])
    b = Task("B", say, [{"message": "This is task B!"}])
    c = Task("C", say, [{"message": "This is task C!"}])
    d = Task("D", say, [{"message": "This is task D!"}])

    a >> b
    a >> c
    b >> d
    c >> d

w.create()
