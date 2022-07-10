"""
This example showcases how to set a retry on a task. The retry will make the task back off for 5 seconds
post-failure and allow the retries to occur over a duration of 60 seconds.
"""
from hera import Retry, Task, Workflow, WorkflowService


def random_fail():
    import random

    p = random.random()
    if p < 0.5:
        raise Exception("p < .5 = FAIL")
    print("p >= .5 = SUCCESS")


with Workflow("retry", service=WorkflowService(host="my-argo-server.com", token="my-auth-token")) as w:
    Task("fail", random_fail, retry=Retry(duration=5, max_duration=60))

w.create()
