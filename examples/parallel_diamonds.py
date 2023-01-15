"""This example showcases how one can schedule a diamond structure with parallel processing through Hera"""
from hera import Task, Workflow


def say(message: str):
    print(message)


with Workflow("parallel-diamonds") as w:
    (
        Task(
            "a",
            say,
            [{"message": "This is task A.1!"}, {"message": "This is task A.2!"}, {"message": "This is task A.3!"}],
        )
        >> Task(
            "b",
            say,
            [{"message": "This is task B.1!"}, {"message": "This is task B.2!"}, {"message": "This is task B.3!"}],
        )
        >> Task(
            "c",
            say,
            [{"message": "This is task C.1!"}, {"message": "This is task C.2!"}, {"message": "This is task C.3!"}],
        )
        >> Task(
            "d",
            say,
            [{"message": "This is task D.1!"}, {"message": "This is task D.2!"}, {"message": "This is task D.3!"}],
        )
    )

w.create()
