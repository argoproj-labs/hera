"""
This example showcases the classic diamond workflow that is used as an example by Argo documentation and
other libraries.
"""
from hera import Task, Workflow


def say(message: str):
    print(message)


# assumes you used `hera.set_global_token` and `hera.set_global_host` so that the workflow can be submitted
with Workflow("diamond") as w:
    a = Task("a", say, ["This is task A!"])
    b = Task("b", say, ["This is task B!"])
    c = Task("c", say, ["This is task C!"])
    d = Task("d", say, ["This is task D!"])

    a >> b
    a >> c
    b >> d
    c >> d

w.create()
