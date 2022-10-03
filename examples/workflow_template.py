"""This example showcases the classic conditional workflow coin-flip."""

from hera import Task, WorkflowTemplate


def random_code():
    import random

    res = "heads" if random.randint(0, 1) == 0 else "tails"
    print(res)


def heads():
    print("it was heads")


def tails():
    print("it was tails")


with WorkflowTemplate("workflow-template") as w:
    r = Task("r", random_code)
    Task("h", heads).on_other_result(r, "heads")
    Task("t", tails).on_other_result(r, "tails")

w.create()
